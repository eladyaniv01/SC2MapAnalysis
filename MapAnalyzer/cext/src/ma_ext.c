#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <stdlib.h>
#include <numpy/arrayobject.h>
#include <math.h>

//The difference between levels of terrain in height maps
#define LEVEL_DIFFERENCE 16

#define SQRT2 1.41421f

#define HEADER_SIZE sizeof(size_t)

static inline int max_int(int i, int j)
{
    return i < j ? j : i;
}

static inline int min_int(int i, int j)
{
    return i >= j ? j : i;
}

static inline float max_float(float i, float j)
{
    return i < j ? j : i;
}

static inline float min_float(float i, float j)
{
    return i >= j ? j : i;
}


/*
These bitflags are used in an array of 8 bit integers
to note which grid points have these properties
*/
enum NodeStatus {
    CLIMBABLE = (1 << 0),
    BORDER = (1 << 1),
    OVERLORD_SPOT = (1 << 2),
    HANDLED_OVERLORD_SPOT = (1 << 3),
    IN_CURRENT_SET = (1 << 4),
};

/*
Memory management in the extension atm happens in a fixed
size region which is allocated when the module is loaded.
The memory is handled with an arena allocator.
The idea basically is to have a buffer large enough that
we can put stuff we need on there and then just reset
a number in the buffer once in the end of the function.
*/
typedef struct MemoryArena {
    uint8_t *base;
    size_t size;
    size_t used;
} MemoryArena;

/*
Sometimes we need memory repetitively only for a short while
in a loop and it happens often enough that we
need to take care of it somehow.
This can be accomplished with

TempAllocation alloc;
StartTemporaryAllocation(&state.function_arena, &alloc);
...
EndTemporaryAllocation(&state.function_arena, &alloc);

This way the arena is reset to the state where it was before
the allocation.
*/
typedef struct TempAllocation {
    size_t previously_used;
} TempAllocation;

typedef struct FloatLine {
    float start[2];
    float end[2];
} FloatLine;

typedef struct IntLine {
    int start[2];
    int end[2];
} IntLine;

/*
Vectors get initialized first and then you can push stuff
on there. They grow themselves if in danger of going above
capacity. They operate in a designated memory arena so
you can have stuff that lasts for the duration of a function
or stuff with a more limited lifetime.
*/
typedef struct VecInt {
    int size;
    int capacity;
    MemoryArena* arena;
    int* items;
} VecInt;

typedef struct VecFloat {
    int size;
    int capacity;
    MemoryArena* arena;
    float* items;
} VecFloat;

typedef struct VecIntLine {
    int size;
    int capacity;
    MemoryArena* arena;
    IntLine* items;
} VecIntLine;

typedef struct Choke {
    FloatLine main_line;
    VecIntLine* lines;
    VecInt* side1;
    VecInt* side2;
    VecInt* pixels;
    float min_length;
} Choke;

typedef struct ChokeLines {
    VecIntLine* lines;
} ChokeLines;

typedef struct VecChoke {
    Choke* items;
    int size;
    int capacity;
    MemoryArena* arena;
} VecChoke;

typedef struct ChokeList {
    Choke* chokes;
} ChokeList;

/*
function_arena is meant to hold things that tend to last for the entire function
temp_arena is for temporary things that need some memory but can be thrown out soon after
*/
typedef struct ExtensionState { 
    MemoryArena function_arena;
    MemoryArena temp_arena;
} ExtensionState;

ExtensionState state;

static void InitializeMemoryArena(MemoryArena *arena, size_t total_size, uint8_t *base)
{
    arena->base = base;
    arena->size = total_size;
    arena->used = 0;
}

/*
This should be called in the end of the functions that get
exported to python for the buffers we used
so they get reset
*/
static void ClearMemoryArena(MemoryArena *arena)
{
    arena->used = 0;
}

/*
This is the main function to use when you want some memory.
For example you could do
int* arr = (int*)PushToMemoryArena(&state.temp_arena, 10*sizeof(int));
arr[0] = 1;
...

Each allocation saves its size in front so we can refer to it later.
*/
static void* PushToMemoryArena(MemoryArena *arena, size_t size)
{
    uint8_t *location = arena->base + arena->used;
    size_t *size_info = (size_t *)location;
    *size_info = size;

    location = location + HEADER_SIZE;
    arena->used += size + HEADER_SIZE;
    
    memset(location, 0, size);
    return location;
}

static void RemoveFromMemoryArena(MemoryArena *arena, uint8_t *base)
{
    if (base)
    {
        size_t * ptr_cast = (size_t *)base;
        ptr_cast--;
        size_t allocation_size = *ptr_cast;

        if (arena->base + arena->used == base + allocation_size)
        {
            arena->used -= (allocation_size + HEADER_SIZE);
        }
    }
}

/*
In case we need more space we first try to grow the allocation in place
if this was the last thing added. If it was not, we move
the entire thing to a new location and leave the old thing in place.
It will get removed later on when the buffer gets reset.
*/
static void* ReallocInMemoryArena(MemoryArena *arena, uint8_t *current_base, size_t new_size)
{
    if (!current_base)
    {
        return PushToMemoryArena(arena, new_size);
    }
    else
    {
        size_t *ptr_cast = (size_t*)current_base;
        ptr_cast--;
        size_t cur_size = *ptr_cast;

        if (current_base + cur_size == arena->base + arena->used)
        {
            *ptr_cast = new_size;

            arena->used += new_size - cur_size;
            return current_base;
        }
        else
        {
            void *new_base = PushToMemoryArena(arena, new_size);
            memcpy(new_base, current_base, cur_size);
            return new_base;
        }
    }
}

static void StartTemporaryAllocation(MemoryArena *arena, TempAllocation *temp)
{
    temp->previously_used = arena->used;
}

static void EndTemporaryAllocation(MemoryArena *arena, TempAllocation *temp)
{
    arena->used = temp->previously_used;
}


static VecInt* InitVecInt(MemoryArena *arena, int capacity)
{
    VecInt* vec = (VecInt*)PushToMemoryArena(arena, sizeof(VecInt) + capacity*sizeof(int));
    uint8_t *base = (uint8_t*)vec;
    base += sizeof(VecInt);
    vec->items = (int*)base; 
    vec->size = 0;
    vec->capacity = capacity;
    vec->arena = arena;
    return vec;
}

static VecInt* PushToVecInt(VecInt* vec, int new)
{
    if (vec->size < vec->capacity)
    {
        vec->items[vec->size] = new;
        ++vec->size;
        return vec;
    }
    else
    {
        size_t new_size = sizeof(VecInt) + 2*vec->capacity*sizeof(int);
        VecInt* return_vec = (VecInt*)ReallocInMemoryArena(vec->arena, (uint8_t*)vec, new_size);

        uint8_t *base = (uint8_t*)return_vec;
        base += sizeof(VecInt);
        return_vec->items = (int*)base; 

        return_vec->capacity = 2*vec->capacity;
        return_vec->items[return_vec->size] = new;
        ++return_vec->size;
        return return_vec;
    }
}

static VecFloat* InitVecFloat(MemoryArena *arena, int capacity)
{
    VecFloat* vec = (VecFloat*)PushToMemoryArena(arena, sizeof(VecFloat) + capacity*sizeof(float));
    uint8_t *base = (uint8_t*)vec;
    base += sizeof(VecFloat);
    vec->items = (float*)base; 
    vec->size = 0;
    vec->capacity = capacity;
    vec->arena = arena;
    return vec;
}

static VecFloat* PushToVecFloat(VecFloat* vec, float new)
{
    if (vec->size < vec->capacity)
    {
        vec->items[vec->size] = new;
        ++vec->size;
        return vec;
    }
    else
    {
        size_t new_size = sizeof(VecFloat) + 2*vec->capacity*sizeof(float);
        VecFloat* return_vec = (VecFloat*)ReallocInMemoryArena(vec->arena, (uint8_t*)vec, new_size);

        uint8_t *base = (uint8_t*)return_vec;
        base += sizeof(VecFloat);
        return_vec->items = (float*)base; 

        return_vec->capacity = 2*vec->capacity;
        return_vec->items[return_vec->size] = new;
        ++return_vec->size;
        return return_vec;
    }
}

static VecIntLine* InitVecIntLine(MemoryArena *arena, int capacity)
{
    VecIntLine* vec = (VecIntLine*)PushToMemoryArena(arena, sizeof(VecIntLine) + capacity*sizeof(IntLine));
    uint8_t *base = (uint8_t*)vec;
    base += sizeof(VecIntLine);
    vec->items = (IntLine*)base; 
    vec->size = 0;
    vec->capacity = capacity;
    vec->arena = arena;
    return vec;
}

static VecIntLine* PushToVecIntLine(VecIntLine* vec, IntLine new)
{
    if (vec->size < vec->capacity)
    {
        vec->items[vec->size] = new;
        ++vec->size;
        return vec;
    }
    else
    {
        size_t new_size = sizeof(VecIntLine) + 2*vec->capacity*sizeof(IntLine);
        VecIntLine* return_vec = (VecIntLine*)ReallocInMemoryArena(vec->arena, (uint8_t*)vec, new_size);

        uint8_t *base = (uint8_t*)return_vec;
        base += sizeof(VecIntLine);
        return_vec->items = (IntLine*)base; 

        return_vec->capacity = 2*vec->capacity;
        return_vec->items[return_vec->size] = new;
        ++return_vec->size;
        return return_vec;
    }
}


static VecChoke* InitVecChoke(MemoryArena *arena, int capacity)
{
    VecChoke* vec = (VecChoke*)PushToMemoryArena(arena, sizeof(VecChoke) + capacity*sizeof(Choke));
    uint8_t *base = (uint8_t*)vec;
    base += sizeof(VecChoke);
    vec->items = (Choke*)base; 
    vec->size = 0;
    vec->capacity = capacity;
    vec->arena = arena;
    return vec;
}

static VecChoke* PushToVecChoke(VecChoke* vec, Choke new)
{
    if (vec->size < vec->capacity)
    {
        vec->items[vec->size] = new;
        ++vec->size;
        return vec;
    }
    else
    {
        size_t new_size = sizeof(VecChoke) + 2*vec->capacity*sizeof(Choke);
        VecChoke* return_vec = (VecChoke*)ReallocInMemoryArena(vec->arena, (uint8_t*)vec, new_size);

        uint8_t *base = (uint8_t*)return_vec;
        base += sizeof(VecChoke);
        return_vec->items = (Choke*)base; 

        return_vec->capacity = 2*vec->capacity;
        return_vec->items[return_vec->size] = new;
        ++return_vec->size;
        return return_vec;
    }
}

static void RemoveFromVecChoke(VecChoke* vec, int index)
{
    if (index >= 0 && index < vec->size)
    {
        vec->items[index] = vec->items[vec->size - 1];
        --vec->size;
    }
}


/*
idx The index of the node in weight array (w*y+x)
cost Cost this far + estimate cost from here to finish
path_length The path length this far
*/
typedef struct Node {
    int idx;
    float cost;
    int path_length;
} Node;

/*
nodes Array of nodes in the queue. Atm set to the length of the pathing grid so we don't run out of space 
index_map Array for saving where in the queue each index is, used for faster updates
size Current number of nodes in the array
*/
typedef struct PriorityQueue {
    Node* nodes;
    int* index_map;
    int size;
} PriorityQueue;

static inline int tree_parent(int i) 
{ 
    return (i - 1) / 2; 
} 
  
static inline int tree_left_child(int i) 
{ 
    return ((2 * i) + 1); 
} 
  
static inline int tree_right_child(int i) 
{ 
    return ((2 * i) + 2); 
} 

static void queue_swap(PriorityQueue *queue, int i, int j)
{
    Node tmp = queue->nodes[i];
    queue->nodes[i] = queue->nodes[j];
    queue->nodes[j] = tmp;
    queue->index_map[queue->nodes[i].idx] = i;
    queue->index_map[queue->nodes[j].idx] = j;
}

/*
Move a node up the priority queue.
Used when adding a node or updating a cost of one
*/
static void queue_up(PriorityQueue *queue, int index)
{
    Node* nodes = queue->nodes;
    while (index > 0 && nodes[tree_parent(index)].cost > nodes[index].cost)
    {
        queue_swap(queue, tree_parent(index), index); 
        index = tree_parent(index); 
    } 
}

/*
Move a node down the priority queue.
Used when the top node has been removed,
the last node of the queue replaces it and then moves down.
*/
static void queue_down(PriorityQueue *queue, int index)
{
    int min_index = index;
    Node* nodes = queue->nodes;

    for (;;)
    {
        int l = tree_left_child(index); 
  
        if (l < queue->size && nodes[l].cost < nodes[min_index].cost)
        { 
            min_index = l; 
        } 
    
        int r = tree_right_child(index); 
    
        if (r < queue->size && nodes[r].cost < nodes[min_index].cost)
        { 
            min_index = r;
        } 
    
        if (index != min_index)
        {
            queue_swap(queue, index, min_index);
            index = min_index;
        }
        else
        {
            break;
        }
        
    }
}

static void queue_push_or_update(PriorityQueue *queue, Node node)
{
    Node* nodes = queue->nodes;
    if (queue->index_map[node.idx] != -1)
    {
        int idx = queue->index_map[node.idx];
        queue->nodes[idx].cost = node.cost;
        queue->nodes[idx].path_length = node.path_length;
        queue_up(queue, idx);
    }
    else
    {
        ++queue->size;
        nodes[queue->size - 1] = node;
        queue->index_map[node.idx] = queue->size - 1;
        queue_up(queue, queue->size - 1);
    }
    
}

static Node queue_pop(PriorityQueue* queue)
{
    Node node = queue->nodes[0];
    queue->index_map[node.idx] = -1;
    queue->nodes[0] = queue->nodes[queue->size - 1];
    --queue->size;
    queue_down(queue, 0);
    return node;
}

static Node queue_top(PriorityQueue *queue)
{
    return queue->nodes[0];
}

static PriorityQueue* queue_create(MemoryArena *arena, int max_size)
{
    PriorityQueue* queue = (PriorityQueue*) PushToMemoryArena(arena, sizeof(PriorityQueue));
    queue->nodes = (Node*) PushToMemoryArena(arena, max_size*sizeof(Node));
    queue->index_map = (int*) PushToMemoryArena(arena, max_size*sizeof(int));
    queue->size = 0;
    
    return queue;
}

static inline float find_min(float *arr, int length)
{
    float minimum = HUGE_VALF;
    for (int i = 0; i < length; ++i)
    {
        minimum = min_float(arr[i], minimum);
    }
    return minimum;
}

/*
Calculate the estimated cost of moving to a point along a grid.
Baseline should be the minimum weight in the grid so the
heuristic remains consistent.
*/
static inline float distance_heuristic(int x0, int y0, int x1, int y1, float baseline)
{
    return baseline*(max_int(abs(x0 - x1), abs(y0 - y1)) + (SQRT2 - 1) * min_int(abs(x0 - x1), abs(y0 - y1)));
}

static inline float euclidean_distance(int x0, int y0, int x1, int y1)
{
    return (float)sqrt((double)((x0 - x1)*(x0 - x1) + (y0 - y1)*(y0 - y1)));
}

/*
Run the astar algorithm. The resulting path is saved in paths
so each node knows the previous node and the path can be traced back.
Returns the path length.
*/
static int run_pathfind(MemoryArena *arena, float *weights, int* paths, int w, int h, int start, int goal)
{
    float weight_baseline = find_min(weights, w*h);
    
    int path_length = -1;

    TempAllocation temp_alloc;
    StartTemporaryAllocation(arena, &temp_alloc);

    PriorityQueue *nodes_to_visit = queue_create(arena, w*h);

    Node start_node = { start, 0.0f, 1 };
    float *costs = (float*) PushToMemoryArena(arena, w*h*sizeof(float));

    for (int i = 0; i < w*h; ++i)
    {
        costs[i] = HUGE_VALF;
        nodes_to_visit->index_map[i] = -1;
    }
    
    costs[start] = 0;

    queue_push_or_update(nodes_to_visit, start_node);

    int nbrs[8];

    while (nodes_to_visit->size > 0)
    {
        Node cur = queue_pop(nodes_to_visit);
        if (cur.idx == goal)
        {
            path_length = cur.path_length;
            break;
        }

        int row = cur.idx / w;
        int col = cur.idx % w;

        nbrs[0] = (row > 0) ? cur.idx - w : -1;
        nbrs[1] = (col > 0) ? cur.idx - 1 : -1;
        nbrs[2] = (col + 1 < w) ? cur.idx + 1 : -1;
        nbrs[3] = (row + 1 < h) ? cur.idx + w : -1;
        nbrs[4] = (row > 0 && col > 0) ? cur.idx - w - 1 : -1;
        nbrs[5] = (row + 1 < h && col > 0) ? cur.idx + w - 1 : -1;
        nbrs[6] = (row > 0 && col + 1 < w) ? cur.idx - w + 1 : -1;
        nbrs[7] = (row + 1 < h && col + 1 < w) ? cur.idx + w + 1 : -1;

        float heuristic_cost;

        for (int i = 0; i < 8; ++i)
        {
            if (nbrs[i] >= 0)
            {
                float new_cost = costs[cur.idx];
                if (i < 4)
                {
                    new_cost += weights[nbrs[i]];
                }
                else
                {
                    new_cost += weights[nbrs[i]] * SQRT2;
                }
                if (new_cost < costs[nbrs[i]])
                {
                    
                    heuristic_cost = distance_heuristic(nbrs[i] / w, nbrs[i] % w, goal / w, goal % w, weight_baseline);
                    
                    float estimated_cost = new_cost + heuristic_cost;
                    Node new_node = { nbrs[i], estimated_cost, cur.path_length + 1};
                    queue_push_or_update(nodes_to_visit, new_node);

                    costs[nbrs[i]] = new_cost;
                    paths[nbrs[i]] = cur.idx;
                }    
            }
        }
    }
    
    EndTemporaryAllocation(arena, &temp_alloc);

    return path_length;
}

/*
Estimating a straight line weight over multiple nodes.
Used in path smoothing where we remove nodes if we can jump
ahead some nodes in a straight line with a lower cost.
*/
static float calculate_line_weight(MemoryArena *arena, float* weights, int w, int x0, int y0, int x1, int y1)
{
    float flight_distance = euclidean_distance(x0, y0, x1, y1);
    
    TempAllocation temp_alloc;
    StartTemporaryAllocation(arena, &temp_alloc);

    VecInt *line_coords = InitVecInt(arena, (int)flight_distance*2);

    int step_constant = 5;
    float step_constant_inverse = (float) 1 / step_constant;

    int dots = step_constant*(int)flight_distance;

    float dir_vec[2] = { (x1 - x0) / flight_distance, (y1 - y0) / flight_distance };

    for (int i = 0; i < dots; ++i)
    {
        int current_x = (int)(x0 + dir_vec[0]*i*step_constant_inverse);
        int current_y = (int)(y0 + dir_vec[1]*i*step_constant_inverse);

        int added_already = 0;
        for (int j = 0; j < line_coords->size; ++j)
        {
            if (line_coords->items[j] == w*current_y + current_x)
            {
                added_already = 1;
            }
        }

        if (!added_already)
        {
            line_coords = PushToVecInt(line_coords, w*current_y + current_x);
        }
    }

    float norm = 0.0f;
    if (line_coords->size > 0)
    {
        norm = flight_distance / line_coords->size; 
    }

    float weight_sum = 0.0f;
    for (int i = 0; i < line_coords->size; ++i)
    {
        weight_sum += weights[line_coords->items[i]];
        if(weight_sum >= HUGE_VALF) break;
    }

    EndTemporaryAllocation(arena, &temp_alloc);

    return weight_sum*norm;
}

/*
Exported function to run astar from python.
Takes in grid weights, dimensions of the grid, requested start and end
and whether to smooth the final path.
*/
static PyObject* astar(PyObject *self, PyObject *args)
{
    PyArrayObject* weights_object;
    int h, w, start, goal, smoothing;
    
    
    if (!PyArg_ParseTuple(args, "Oiiiii", &weights_object, &h, &w, &start, &goal, &smoothing))
    {
        return NULL;
    }

    float *weights = (float *)weights_object->data;
    int *paths = (int*) PushToMemoryArena(&state.function_arena, w*h*sizeof(int));

    int path_length = run_pathfind(&state.function_arena, weights, paths, w, h, start, goal);
    
    PyObject *return_val;
    if (path_length >= 0)
    {
        if (!smoothing || path_length < 3)
        {
            npy_intp dims[2] = {path_length, 2};
            PyArrayObject *path = (PyArrayObject*) PyArray_SimpleNew(2, dims, NPY_INT32);
            npy_int32 *path_data = (npy_int32*)path->data;

            int idx = goal;

            for (npy_intp i = dims[0] - 1; i >= 0; --i)
            {
                path_data[2*i] = idx / w;
                path_data[2*i + 1] = idx % w;

                idx = paths[idx];
            }
            return_val = PyArray_Return(path);
        }
        else
        {
            VecInt *smoothed_path_inverted = InitVecInt(&state.function_arena, path_length);

            smoothed_path_inverted = PushToVecInt(smoothed_path_inverted, goal);

            int current_node = paths[goal];
            float step_weight = 0;
            float segment_total_weight = 0;
            for(int i = 1; i < path_length - 1; ++i)
            {
                int next_node = paths[current_node];
                step_weight = weights[next_node] * euclidean_distance(current_node % w, current_node / w, next_node % w, next_node / w);
                segment_total_weight += step_weight;

                int last_added_new_path_node = smoothed_path_inverted->items[smoothed_path_inverted->size - 1];
                int x0 = last_added_new_path_node % w;
                int y0 = last_added_new_path_node / w;
                int x1 = next_node % w;
                int y1 = next_node / w;
                if (calculate_line_weight(&state.function_arena, weights, w, x0, y0, x1, y1) > segment_total_weight * 1.002f)
                {
                    segment_total_weight = step_weight;
                    smoothed_path_inverted = PushToVecInt(smoothed_path_inverted, current_node);
                }

                current_node = next_node;
            }
            smoothed_path_inverted = PushToVecInt(smoothed_path_inverted, start);

            npy_intp dims[2] = {smoothed_path_inverted->size, 2};
            PyArrayObject *path = (PyArrayObject*) PyArray_SimpleNew(2, dims, NPY_INT32);
            npy_int32 *path_data = (npy_int32*)path->data;

            int idx = goal;

            for (npy_intp i = dims[0] - 1; i >= 0; --i)
            {
                path_data[2*i] = smoothed_path_inverted->items[dims[0] - 1 - i] / w;
                path_data[2*i + 1] = smoothed_path_inverted->items[dims[0] - 1 - i] % w;

                idx = paths[idx];
            }
            return_val = PyArray_Return(path);
        }
    }
    else
    {
        return_val = Py_BuildValue("");
    }

    ClearMemoryArena(&state.function_arena);
    ClearMemoryArena(&state.temp_arena);

    return return_val;
}

typedef struct KeyContainer
{
    VecInt *keys;
} KeyContainer;

static int flood_fill_overlord(uint8_t *heights, uint8_t *point_status, int grid_width, int grid_height, int x, int y, uint8_t target_height, uint8_t replacement, KeyContainer* current_set)
{
    int key = y*grid_width + x;
    
    if (point_status[key] & IN_CURRENT_SET) return 1;

    current_set->keys = PushToVecInt(current_set->keys, key);
    point_status[key] |= IN_CURRENT_SET;

    if (target_height != heights[key])
    {
        if (target_height < heights[key] + LEVEL_DIFFERENCE)
        {
            return 0;
        }
        else
        {
            return 1;
        }
    }

    int result = 1;
    if (replacement)
    {
        point_status[key] |= OVERLORD_SPOT;
    }
    else
    {
        point_status[key] &= ~OVERLORD_SPOT;
    }

    if (y > 0)
    {
        result &= flood_fill_overlord(heights, point_status, grid_width, grid_height, x, y - 1, target_height, replacement, current_set);
    }
    if (x > 0)
    {
        result &= flood_fill_overlord(heights, point_status, grid_width, grid_height, x - 1, y, target_height, replacement, current_set);
    }
    if (y < grid_height - 1)
    {
        result &= flood_fill_overlord(heights, point_status, grid_width, grid_height, x, y + 1, target_height, replacement, current_set);
    }
    if (x < grid_width - 1)
    {
        result &= flood_fill_overlord(heights, point_status, grid_width, grid_height, x + 1, y, target_height, replacement, current_set);
    }
    return result;
}

static VecInt* get_nodes_within_distance(MemoryArena *arena, float* weights, int w, int h, int x, int y, float max_distance)
{
    PriorityQueue *nodes_to_visit = queue_create(arena, w*h);

    int start = w*y + x;
    Node start_node = { start, 0.0f, 1 };
    float *costs = (float*) PushToMemoryArena(arena, w*h*sizeof(float));

    for (int i = 0; i < w*h; ++i)
    {
        costs[i] = HUGE_VALF;
        nodes_to_visit->index_map[i] = -1;
    }
    
    costs[start] = 0;

    queue_push_or_update(nodes_to_visit, start_node);

    int nbrs[8];

    VecInt *nodes_within_reach = InitVecInt(arena, min_int(200, (int)(max_distance * max_distance)));

    while (nodes_to_visit->size > 0)
    {
        Node cur = queue_pop(nodes_to_visit);
        nodes_within_reach = PushToVecInt(nodes_within_reach, cur.idx);

        int row = cur.idx / w;
        int col = cur.idx % w;

        nbrs[0] = (row > 0) ? cur.idx - w : -1;
        nbrs[1] = (col > 0) ? cur.idx - 1 : -1;
        nbrs[2] = (col + 1 < w) ? cur.idx + 1 : -1;
        nbrs[3] = (row + 1 < h) ? cur.idx + w : -1;
        nbrs[4] = (row > 0 && col > 0) ? cur.idx - w - 1 : -1;
        nbrs[5] = (row + 1 < h && col > 0) ? cur.idx + w - 1 : -1;
        nbrs[6] = (row > 0 && col + 1 < w) ? cur.idx - w + 1 : -1;
        nbrs[7] = (row + 1 < h && col + 1 < w) ? cur.idx + w + 1 : -1;

        for (int i = 0; i < 8; ++i)
        {
            if (nbrs[i] >= 0)
            {
                float new_cost = costs[cur.idx];
                if (i < 4)
                {
                    new_cost += weights[nbrs[i]];
                }
                else
                {
                    new_cost += weights[nbrs[i]] * SQRT2;
                }
                if (new_cost < costs[nbrs[i]])
                {
                    costs[nbrs[i]] = new_cost;
                    
                    if (costs[nbrs[i]] <= max_distance)
                    {
                        Node new_node = { nbrs[i], new_cost, cur.path_length + 1};
                        queue_push_or_update(nodes_to_visit, new_node);
                    }
                }    
            }
        }
    }

    return nodes_within_reach;
}


/*
Initialize a choke based on a single line
*/
static Choke choke_create_based_on_line(IntLine line)
{
    Choke choke = { 0 };
    choke.main_line.start[0] = (float)line.start[0];
    choke.main_line.start[1] = (float)line.start[1];
    choke.main_line.end[0] = (float)line.end[0];
    choke.main_line.end[1] = (float)line.end[1];

    choke.lines = InitVecIntLine(&state.function_arena, 50);
    choke.lines = PushToVecIntLine(choke.lines, line);

    choke.side1 = InitVecInt(&state.function_arena, 50);
    choke.side1 = PushToVecInt(choke.side1, line.start[0]);
    choke.side1 = PushToVecInt(choke.side1, line.start[1]);

    choke.side2 = InitVecInt(&state.function_arena, 50);
    choke.side2 = PushToVecInt(choke.side1, line.end[0]);
    choke.side2 = PushToVecInt(choke.side1, line.end[1]);

    choke.pixels = InitVecInt(&state.function_arena, 100);

    choke.min_length = euclidean_distance(line.start[0], line.start[1], line.end[0], line.end[1]);

    return choke;
}

static void choke_add_line(Choke* choke, IntLine line)
{
    choke->lines = PushToVecIntLine(choke->lines, line);

    int side1_contains_start = 0;
    int side1_size = choke->side1->size;
    int* side1 = choke->side1->items;

    for(int i = 0; i < side1_size / 2; ++i)
    {
        if (side1[2*i] == line.start[0] && side1[2*i + 1] == line.start[1])
        {
            side1_contains_start = 1;
            break;
        }
    }
    if (side1_contains_start == 0)
    {
        choke->side1 = PushToVecInt(choke->side1, line.start[0]);
        choke->side1 = PushToVecInt(choke->side1, line.start[1]);
    }

    int side2_contains_end = 0;
    int side2_size = choke->side2->size;
    int* side2 = choke->side2->items;

    for(int i = 0; i < side2_size / 2; ++i)
    {
        if (side2[2*i] == line.end[0] && side2[2*i + 1] == line.end[1])
        {
            side2_contains_end = 1;
            break;
        }
    }
    if (side2_contains_end == 0)
    {
        choke->side2 = PushToVecInt(choke->side2, line.end[0]);
        choke->side2 = PushToVecInt(choke->side2, line.end[1]);
    }
}

static void chokes_solve(uint8_t *point_status, float* border_weights, uint8_t *walkable, ChokeLines* choke_lines, int w, int h, int x, int y, int x_start, int y_start, int x_end, int y_end)
{
    float choke_distance = 13.0f;
    float choke_border_distance = 30.0f;

    if (point_status[w*y + x] & BORDER)
    {
        TempAllocation temp_alloc;
        StartTemporaryAllocation(&state.temp_arena, &temp_alloc);

        VecInt* reachable_borders = get_nodes_within_distance(&state.temp_arena, border_weights, w, h, x, y, choke_border_distance);

        int xmin = x;
        int xmax = min_int(x + (int)choke_distance, x_end);
        int ymin = max_int(y - (int)choke_distance, y_start);
        int ymax = min_int(y + (int)choke_distance, y_end);

        for (int ynew = ymin; ynew < ymax; ++ynew)
        {
            for (int xnew = xmin; xnew < xmax; ++xnew)
            {
                if (!(point_status[w*ynew + xnew] & BORDER)) continue;

                float flight_distance = euclidean_distance(x, y, xnew, ynew);
                
                if (flight_distance > choke_distance || flight_distance < 2.0f) continue;
                
                int found = 0;
                for (int i = 0; i < reachable_borders->size; ++i)
                {
                    if (reachable_borders->items[i] == w*ynew + xnew)
                    {
                        found = 1;
                        break;
                    }
                }

                if (found) continue;

                int dots = (int)flight_distance;
                float unit_vector[2] = { (float)(xnew - x) / flight_distance, (float)(ynew - y) / flight_distance };
                int wall_hit = 0;

                for (int i = 1; i < dots; ++i)
                {
                    int draw_x = (int)(x + unit_vector[0]*i);
                    int draw_y = (int)(y + unit_vector[1]*i);

                    if ((draw_x == x && draw_y == y) || (draw_x == xnew && draw_y == ynew))
                    {
                        continue;
                    }

                    if (walkable[draw_y*w + draw_x] == 0)
                    {
                        wall_hit = 1;
                        break;
                    }
                }

                if (wall_hit == 0 && dots > 4)
                {
                    float center_x = (xnew + x)*0.5f;
                    float center_y = (ynew + y)*0.5f;
                    float perpendicular_unit_vector[2] = { -unit_vector[1], unit_vector[0] };
                    int half_dots = dots / 2;

                    for (int i = -half_dots; i < half_dots; ++i)
                    {
                        int draw_x = (int)(center_x + perpendicular_unit_vector[0]*i);
                        int draw_y = (int)(center_y + perpendicular_unit_vector[1]*i);

                        if (walkable[w*draw_y + draw_x] == 0)
                        {
                            wall_hit = 1;
                            break;
                        }
                    }
                }

                if (wall_hit == 0)
                {
                    IntLine line;
                    line.start[0] = x;
                    line.start[1] = y;
                    line.end[0] = xnew;
                    line.end[1] = ynew;
                    choke_lines->lines = PushToVecIntLine(choke_lines->lines, line);
                }

            }
        }
        EndTemporaryAllocation(&state.temp_arena, &temp_alloc);
    }
}

static void choke_remove_excess_lines(Choke* choke)
{
    float min_distance = HUGE_VALF;

    TempAllocation temp_alloc;
    StartTemporaryAllocation(&state.temp_arena, &temp_alloc);

    VecFloat *distances = InitVecFloat(&state.temp_arena, choke->lines->size);

    for(int i = 0; i < choke->lines->size; ++i)
    {
        IntLine line = choke->lines->items[i];
        float d = euclidean_distance(line.start[0], line.start[1], line.end[0], line.end[1]);
        distances = PushToVecFloat(distances, d);
        if (d < min_distance)
        {
            min_distance = d;
        }
    }

    VecIntLine *new_lines = InitVecIntLine(&state.function_arena, choke->lines->size);

    for(int i = 0; i < choke->lines->size; ++i)
    {
        if (distances->items[i] <= min_distance + 2.5f)
        {
            new_lines = PushToVecIntLine(new_lines, choke->lines->items[i]);
        }
    }

    EndTemporaryAllocation(&state.temp_arena, &temp_alloc);

    choke->lines = new_lines;
    choke->min_length = min_distance;
}

static void choke_calc_final_line(Choke* choke)
{
    float xsum = 0;
    float ysum = 0;

    int side1_count = choke->side1->size / 2;
    for(int i = 0; i < side1_count; ++i)
    {
        xsum += choke->side1->items[2*i];
        ysum += choke->side1->items[2*i + 1];
    }

    float point1[2] = { xsum / side1_count, ysum / side1_count };

    xsum = 0;
    ysum = 0;

    int side2_count = choke->side2->size / 2;
    for(int i = 0; i < side2_count; ++i)
    {
        xsum += choke->side2->items[2*i];
        ysum += choke->side2->items[2*i + 1];
    }

    float point2[2] = { xsum / side2_count, ysum / side2_count };

    choke->main_line.start[0] = point1[0];
    choke->main_line.start[1] = point1[1];
    choke->main_line.end[0] = point2[0];
    choke->main_line.end[1] = point2[1];
}

static void choke_set_pixels(Choke* choke)
{
    for (int l = 0; l < choke->lines->size; ++l)
    {
        IntLine line = choke->lines->items[l];
        float flight_distance = euclidean_distance(line.start[0], line.start[1], line.end[0], line.end[1]);
        int dots = (int)flight_distance;
        float unit_vector[2] = { (line.end[0] - line.start[0]) / flight_distance, (line.end[1] - line.start[1]) / flight_distance };
        
        for (int i = 1; i < dots*2; ++i)
        {
            int draw_x = (int)(line.start[0] + unit_vector[0]* i * 0.5f);
            int draw_y = (int)(line.start[1] + unit_vector[1]* i * 0.5f);

            if ((draw_x == line.start[0] && draw_y == line.start[1]) || (draw_x == line.end[0] && draw_y == line.end[1]))
            {
                continue;
            }

            int contained = 0;

            for(int j = 0; j < choke->pixels->size / 2; ++j)
            {
                if (choke->pixels->items[2*j] == draw_x && choke->pixels->items[2*j + 1] == draw_y)
                {
                    contained = 1;
                    break;
                }
            }

            if(!contained)
            {
                choke->pixels = PushToVecInt(choke->pixels, draw_x);
                choke->pixels = PushToVecInt(choke->pixels, draw_y);
            }
        }
    }
}

static VecChoke* chokes_group(ChokeLines* choke_lines)
{
    VecChoke *list = InitVecChoke(&state.function_arena, 100);

    int line_count = choke_lines->lines->size;
    TempAllocation temp_alloc;
    StartTemporaryAllocation(&state.temp_arena, &temp_alloc);
    uint8_t *used_indices = (uint8_t*)PushToMemoryArena(&state.temp_arena, line_count*sizeof(uint8_t));

    for (int i = 0; i < line_count; ++i)
    {
        if (used_indices[i]) continue;

        used_indices[i] = 1;

        Choke current_choke = choke_create_based_on_line(choke_lines->lines->items[i]);

        int last_line_count = 0;
        int current_line_count = current_choke.lines->size;
        
        while (last_line_count < current_line_count)
        {
            for (int j = i + 1; j < line_count; ++j)
            {
                if (used_indices[j]) continue;

                IntLine check_line = choke_lines->lines->items[j];
                for (int k = 0; k < current_choke.side1->size / 2; ++k)
                {
                    int point_x = current_choke.side1->items[2*k];
                    int point_y = current_choke.side1->items[2*k + 1];

                    int added = 0;

                    if (distance_heuristic(check_line.start[0], check_line.start[1], point_x, point_y, 1) <= SQRT2)
                    {
                        for (int l = 0; l < current_choke.side2->size / 2; ++l)
                        {
                            int point2_x = current_choke.side2->items[2*l];
                            int point2_y = current_choke.side2->items[2*l + 1];

                            if (distance_heuristic(check_line.end[0], check_line.end[1], point2_x, point2_y, 1) <= SQRT2)
                            {
                                used_indices[j] = 1;

                                if (distance_heuristic(check_line.start[0], check_line.start[1], point_x, point_y, 1) > 0 || distance_heuristic(check_line.end[0], check_line.end[1], point2_x, point2_y, 1) > 0)
                                {
                                    choke_add_line(&current_choke, check_line);
                                    added = 1;
                                }
                                break;
                            }

                        }
                    }

                    if (distance_heuristic(check_line.end[0], check_line.end[1], point_x, point_y, 1) <= SQRT2)
                    {
                        for (int l = 0; l < current_choke.side2->size / 2; ++l)
                        {
                            int point2_x = current_choke.side2->items[2*l];
                            int point2_y = current_choke.side2->items[2*l + 1];

                            if (distance_heuristic(check_line.start[0], check_line.start[1], point2_x, point2_y, 1) <= SQRT2)
                            {
                                used_indices[j] = 1;

                                if (distance_heuristic(check_line.end[0], check_line.end[1], point_x, point_y, 1) > 0 && distance_heuristic(check_line.start[0], check_line.start[1], point2_x, point2_y, 1) > 0)
                                {
                                    IntLine line_to_add = { { check_line.end[0], check_line.end[1] }, { check_line.start[0], check_line.start[1] }};
                                    choke_add_line(&current_choke, line_to_add);
                                    added = 1;
                                }
                                break;

                            }
                        }
                    }

                    if (added == 1)
                    {
                        break;
                    }
                }
            }
            last_line_count = current_line_count;
            current_line_count = current_choke.lines->size;
        }
        list = PushToVecChoke(list, current_choke);
    }

    EndTemporaryAllocation(&state.temp_arena, &temp_alloc);

    int i = 0;
    while(i < list->size)
    {
        choke_remove_excess_lines(&list->items[i]);
        choke_calc_final_line(&list->items[i]);

        if (list->items[i].lines->size < 4)
        {
            RemoveFromVecChoke(list, i);
        }
        else
        {
            choke_set_pixels(&list->items[i]);
            ++i;
        }
    }
    
    return list;
}

static PyObject* choke_list_to_pyobject(VecChoke *list)
{

    int choke_count = list->size;

    PyObject* return_list = PyList_New(choke_count);

    for(int i = 0; i < choke_count; ++i)
    {
        Choke choke = list->items[i];

        PyObject *py_choke = PyTuple_New(6);

        PyObject *py_main_line = PyTuple_New(2);
        PyObject *py_lines = PyList_New(choke.lines->size);
        PyObject *py_side1 = PyList_New(choke.side1->size / 2);
        PyObject *py_side2 = PyList_New(choke.side2->size / 2);
        PyObject *py_pixels = PyList_New(choke.pixels->size / 2);
        PyObject *py_min_length = PyFloat_FromDouble((double)choke.min_length);
        
        PyObject* main_line_start = PyTuple_New(2);
        PyTuple_SetItem(main_line_start, 0, PyFloat_FromDouble((double)choke.main_line.start[1]));
        PyTuple_SetItem(main_line_start, 1, PyFloat_FromDouble((double)choke.main_line.start[0]));

        PyObject* main_line_end = PyTuple_New(2);
        PyTuple_SetItem(main_line_end, 0, PyFloat_FromDouble((double)choke.main_line.end[1]));
        PyTuple_SetItem(main_line_end, 1, PyFloat_FromDouble((double)choke.main_line.end[0]));

        PyTuple_SetItem(py_main_line, 0, main_line_start);
        PyTuple_SetItem(py_main_line, 1, main_line_end);

        for (int j = 0; j < choke.lines->size; ++j)
        {
            PyObject* cur = PyTuple_New(2);
            
            PyObject* first_tuple = PyTuple_New(2);
            PyTuple_SetItem(first_tuple, 0, PyLong_FromLong(choke.lines->items[j].start[1]));
            PyTuple_SetItem(first_tuple, 1, PyLong_FromLong(choke.lines->items[j].start[0]));
            
            PyObject* second_tuple = PyTuple_New(2);
            PyTuple_SetItem(second_tuple, 0, PyLong_FromLong(choke.lines->items[j].end[1]));
            PyTuple_SetItem(second_tuple, 1, PyLong_FromLong(choke.lines->items[j].end[0]));
            
            PyTuple_SetItem(cur, 0, first_tuple);
            PyTuple_SetItem(cur, 1, second_tuple);

            PyList_SetItem(py_lines, j, cur);
        }

        for (int j = 0; j < choke.side1->size / 2; ++j)
        {
            PyObject *cur = PyTuple_New(2);
            PyTuple_SetItem(cur, 0, PyLong_FromLong(choke.side1->items[2*j + 1]));
            PyTuple_SetItem(cur, 1, PyLong_FromLong(choke.side1->items[2*j]));

            PyList_SetItem(py_side1, j, cur);
        }
        
        for (int j = 0; j < choke.side2->size / 2; ++j)
        {
            PyObject *cur = PyTuple_New(2);
            PyTuple_SetItem(cur, 0, PyLong_FromLong(choke.side2->items[2*j + 1]));
            PyTuple_SetItem(cur, 1, PyLong_FromLong(choke.side2->items[2*j]));

            PyList_SetItem(py_side2, j, cur);
        }

        for (int j = 0; j < choke.pixels->size / 2; ++j)
        {
            PyObject *cur = PyTuple_New(2);
            PyTuple_SetItem(cur, 0, PyLong_FromLong(choke.pixels->items[2*j + 1]));
            PyTuple_SetItem(cur, 1, PyLong_FromLong(choke.pixels->items[2*j]));

            PyList_SetItem(py_pixels, j, cur);
        }

        PyTuple_SetItem(py_choke, 0, py_main_line);
        PyTuple_SetItem(py_choke, 1, py_lines);
        PyTuple_SetItem(py_choke, 2, py_side1);
        PyTuple_SetItem(py_choke, 3, py_side2);
        PyTuple_SetItem(py_choke, 4, py_pixels);
        PyTuple_SetItem(py_choke, 5, py_min_length);

        PyList_SetItem(return_list, i, py_choke);
    }

    return return_list;
}

/*
Calculate choke points, overlord spots and spots that are
pathable for reapers and other climber units but aren't for regular ones
Based on https://github.com/DrInfy/sc2-pathlib
*/
static PyObject* get_map_data(PyObject *self, PyObject *args)
{
    PyArrayObject* walkable_object;
    PyArrayObject* heights_object;
    int h, w, y_start, y_end, x_start, x_end;
    
    if (!PyArg_ParseTuple(args, "OOiiiiii", &walkable_object, &heights_object, &h, &w, &y_start, &y_end, &x_start, &x_end))
    {
        return NULL;
    }

    uint8_t *walkable = (uint8_t *)walkable_object->data;
    uint8_t *heights = (uint8_t *)heights_object->data;

    uint8_t *point_status = (uint8_t *)PushToMemoryArena(&state.function_arena, w*h*sizeof(uint8_t));
    float *choke_weights = (float *)PushToMemoryArena(&state.function_arena, w*h*sizeof(float));

    for ( int i = 0; i < w*h; ++i)
    {
        choke_weights[i] = HUGE_VALF;
    }

    int dirs[8] = { -1, -1, 1, -1, 1, 0, 0, 1 };

    for (int y = 0; y < h; ++y)
    {
        for (int x = 0; x < w; ++x)
        {
            
            if (x == x_start - 1 || x == x_end || y == y_start - 1 || y == y_end)
            {
                choke_weights[w*y + x] = 1.0f;
            }

            if (y < 2 || x < 2 || y >= h - 2 || x >= w - 2) continue;

            if (walkable[w*y + x] == 0)
            {
                uint8_t h0 = heights[w*y + x + 1];
                uint8_t h1 = heights[w*y + x - 1];
                uint8_t hxy = heights[w*y + x];

                if ((hxy >= h0 + LEVEL_DIFFERENCE && h0 > 0) || (hxy >= h1 + LEVEL_DIFFERENCE && h1 > 0))
                {
                    point_status[w*y + x] |= OVERLORD_SPOT;
                }

                int nbr1 = w*(y + 1) + x + 1;
                int nbr2 = w*(y + 1) + x - 1;
                int nbr3 = w*y + x + 1;
                int nbr4 = w*y + x - 1;
                int nbr5 = w*(y - 1) + x + 1;
                int nbr6 = w*(y - 1) + x - 1;
                int nbr7 = w*(y + 1) + x;
                int nbr8 = w*(y - 1) + x;

                if (walkable[nbr1]
                    || walkable[nbr2]
                    || walkable[nbr3]
                    || walkable[nbr4]
                    || walkable[nbr5]
                    || walkable[nbr6]
                    || walkable[nbr7]
                    || walkable[nbr8])
                {
                    choke_weights[w*y + x] = 1.0f;
                    point_status[w*y + x] |= BORDER;
                }

                continue;
            }
            
            for (int d = 0; d < 4; ++d)
            {
                int xdir = dirs[2*d];
                int ydir = dirs[2*d + 1];

                int x0 = x;
                int y0 = y;
                int x1 = x + xdir;
                int y1 = y + ydir;
                int x2 = x + xdir * 2;
                int y2 = y + ydir * 2;

                if (walkable[w*y1 + x1] == 1 || walkable[w*y2 + x2] == 0) continue;

                uint8_t h0 = heights[w*(y1 + 1) + x1];
                uint8_t h1 = heights[w*(y1 + 1) + x1 + 1];
                uint8_t h2 = heights[w*y1 + x1];
                uint8_t h3 = heights[w*y1 + x1 + 1];

                if (xdir != 0 && ydir != 0)
                {
                    if (xdir == ydir)
                    {
                        if ((h0 == h1 || h0 == h2) && h2 == h1 + LEVEL_DIFFERENCE && h0 == h3)
                        {
                            point_status[w*y1 + x1] |= CLIMBABLE;
                        }
                        else if ((h0 == h1 && h0 == h3 && h0 == h2 + LEVEL_DIFFERENCE) || (h0 == h2 && h0 == h3 && h1 == h2 + LEVEL_DIFFERENCE))
                        {
                            point_status[w*y1 + x1] |= CLIMBABLE;
                        }
                    }
                    else
                    {
                        if ((h1 == h2 && h1 == h3 && h1 == h0 + LEVEL_DIFFERENCE) || (h0 == h1 && h0 == h2 && h3 == h0 + LEVEL_DIFFERENCE))
                        {
                            point_status[w*y1 + x1] |= CLIMBABLE;
                        }
                        else if((h0 == h1 && h0 == h2 && h0 == h3 + LEVEL_DIFFERENCE) || (h1 == h2 && h1 == h3 && h0 == h3 + LEVEL_DIFFERENCE))
                        {
                            point_status[w*y1 + x1] |= CLIMBABLE;
                        }
                    }
                }
                else
                {
                    if (xdir != 0)
                    {
                        if (h0 == h2 && h1 == h3 && h0 + LEVEL_DIFFERENCE == h1)
                        {
                            point_status[w*y1 + x1] |= CLIMBABLE;
                        }
                        else if(h0 == h2 && h1 == h3 && h0 == h1 + LEVEL_DIFFERENCE)
                        {
                            point_status[w*y1 + x1] |= CLIMBABLE;
                        }
                    }   
                    else if(ydir != 0)
                    {
                        if (h0 == h1 && h2 == h3 && h0 + LEVEL_DIFFERENCE == h2)
                        {
                            point_status[w*y1 + x1] |= CLIMBABLE;
                        }
                        else if (h0 == h1 && h2 == h3 && h0 == h2 + LEVEL_DIFFERENCE)
                        {
                            point_status[w*y1 + x1] |= CLIMBABLE;
                        }
                    }    
                }
            }
        }
    }

    VecFloat *overlord_spot_arr = InitVecFloat(&state.function_arena, 60);

    npy_intp climber_dims[2] = {h, w};
    PyArrayObject *climber_mat = (PyArrayObject*) PyArray_ZEROS(2, climber_dims, NPY_FLOAT32, 0);

    ChokeLines choke_lines = { NULL };
    choke_lines.lines = InitVecIntLine(&state.function_arena, 1000);

    for (int y = y_start; y < y_end; ++y)
    {
        for (int x = x_start; x < x_end; ++x)
        {
            if (point_status[w*y + x] & CLIMBABLE
                && (point_status[w*y + x + 1] & CLIMBABLE
                    || point_status[w*y + x - 1] & CLIMBABLE
                    || point_status[w*(y + 1) + x] & CLIMBABLE
                    || point_status[w*(y - 1) + x] & CLIMBABLE))
            {
                npy_float32 *ptr = (npy_float32*) (climber_mat->data + y * climber_mat->strides[0] + x * climber_mat->strides[1]);
                *ptr = 1.0f;
            }

            int key = w*y + x;
            
            if (!(point_status[key] & HANDLED_OVERLORD_SPOT) && (point_status[key] & OVERLORD_SPOT))
            {
                uint8_t target_height = heights[key];
                KeyContainer c = { NULL };
                TempAllocation temp_alloc;
                StartTemporaryAllocation(&state.temp_arena, &temp_alloc);
                c.keys = InitVecInt(&state.temp_arena, 200);
                if (flood_fill_overlord(heights, point_status, w, h, x, y, target_height, 1, &c) == 1)
                {
                    float spot[2] = { 0.0f, 0.0f };

                    for(int i = 0; i < c.keys->size; ++i)
                    {
                        point_status[c.keys->items[i]] |= HANDLED_OVERLORD_SPOT;
                        int cx = c.keys->items[i] % w;
                        int cy = c.keys->items[i] / w;
                        spot[0] += cx;
                        spot[1] += cy;

                        point_status[c.keys->items[i]] &= ~IN_CURRENT_SET;
                    }

                    spot[0] = spot[0] / (float)c.keys->size;
                    spot[1] = spot[1] / (float)c.keys->size;
                    overlord_spot_arr = PushToVecFloat(overlord_spot_arr, spot[1]);
                    overlord_spot_arr = PushToVecFloat(overlord_spot_arr, spot[0]);

                    c.keys->size = 0;
                }
                else
                {
                    for(int i = 0; i < c.keys->size; ++i)
                    {
                        point_status[c.keys->items[i]] &= ~IN_CURRENT_SET;
                    }
                    c.keys->size = 0;

                    flood_fill_overlord(heights, point_status, w, h, x, y, target_height, 0, &c);
                }

               
                for(int i = 0; i < c.keys->size; ++i)
                {
                    point_status[c.keys->items[i]] &= ~IN_CURRENT_SET;
                }
                EndTemporaryAllocation(&state.temp_arena, &temp_alloc);

            }

            chokes_solve(point_status, choke_weights, walkable, &choke_lines, w, h, x, y, x_start, y_start, x_end, y_end);
        }
    }

    VecChoke *choke_list = chokes_group(&choke_lines);

    npy_intp overlord_dims[2] = {overlord_spot_arr->size / 2, 2};

    PyArrayObject *overlord_mat = (PyArrayObject*) PyArray_SimpleNew(2, overlord_dims, NPY_FLOAT32);

    npy_float32 *overlord_mat_data = (npy_float32*)overlord_mat->data;
    for(int i = 0; i < overlord_spot_arr->size; ++i)
    {
        overlord_mat_data[i] = overlord_spot_arr->items[i];
    }
    PyObject* return_chokes = choke_list_to_pyobject(choke_list);

    PyObject *return_tuple = PyTuple_New(3);
    PyObject *return_climber = PyArray_Return(climber_mat);
    PyObject *return_overlords = PyArray_Return(overlord_mat);

    PyTuple_SetItem(return_tuple, 0, return_climber);
    PyTuple_SetItem(return_tuple, 1, return_overlords);
    PyTuple_SetItem(return_tuple, 2, return_chokes);

    ClearMemoryArena(&state.function_arena);
    ClearMemoryArena(&state.temp_arena);

    return return_tuple;
}

static PyMethodDef cext_methods[] = {
    {"astar", (PyCFunction)astar, METH_VARARGS, "astar"},
    {"get_map_data", (PyCFunction)get_map_data, METH_VARARGS, "get_map_data"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef cext_module = {
    PyModuleDef_HEAD_INIT,"mapanalyzer_cext", NULL, -1, cext_methods
};

PyMODINIT_FUNC PyInit_mapanalyzerext(void) {
    size_t total_space = 50*1024*1024;
    uint8_t* extension_memory = (uint8_t*)malloc(total_space);
    if(!extension_memory) return NULL;

    size_t function_space = (size_t)(0.8*total_space);
    size_t temp_space = total_space - function_space;

    InitializeMemoryArena(&state.function_arena, function_space, extension_memory);
    InitializeMemoryArena(&state.temp_arena, temp_space, extension_memory + function_space);
    
    import_array();
    return PyModule_Create(&cext_module);
}