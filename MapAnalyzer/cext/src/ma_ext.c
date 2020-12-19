#define PY_SSIZE_T_CLEAN
#include <Python.h> // includes stdlib.h
#include <numpy/arrayobject.h>
#include <math.h>
#include "stretchy_buffer.h"

#define LEVEL_DIFFERENCE 16
#define SQRT2 1.41421f

typedef struct Node {
    int idx;
    float cost;
    int path_length;
} Node;

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

static void queue_up(PriorityQueue *queue, int index)
{
    Node* nodes = queue->nodes;
    while (index > 0 && nodes[tree_parent(index)].cost > nodes[index].cost)
    {
        queue_swap(queue, tree_parent(index), index); 
        index = tree_parent(index); 
    } 
}

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

static PriorityQueue* queue_create(int max_size)
{
    PriorityQueue* queue = (PriorityQueue*) malloc(sizeof(PriorityQueue));
    queue->nodes = (Node*) malloc(max_size*sizeof(Node));
    queue->index_map = (int*) malloc(max_size*sizeof(int));
    queue->size = 0;
    
    return queue;
}

static void queue_delete(PriorityQueue *queue)
{
    free(queue->nodes);
    free(queue->index_map);
    free(queue);
}

static inline float find_min(float *arr, int length)
{
    float minimum = HUGE_VALF;
    for (int i = 0; i < length; ++i)
    {
        minimum = min(arr[i], minimum);
    }
    return minimum;
}

static inline float distance_heuristic(int x0, int y0, int x1, int y1, float baseline)
{
    return baseline*(max(abs(x0 - x1), abs(y0 - y1)) + (SQRT2 - 1) * min(abs(x0 - x1), abs(y0 - y1)));
}

static int run_pathfind(float *weights, int* paths, int w, int h, int start, int goal)
{
    float weight_baseline = find_min(weights, w*h);
    
    int path_length = -1;

    PriorityQueue *nodes_to_visit = queue_create(w*h);

    Node start_node = { start, 0.0f, 1 };
    float *costs = (float*) malloc(w*h*sizeof(float));

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
    
    free(costs);
    queue_delete(nodes_to_visit);

    return path_length;
}

static PyObject* astar(PyObject *self, PyObject *args)
{
    PyArrayObject* weights_object;
    int h, w, start, goal;
    
    if (!PyArg_ParseTuple(args, "Oiiii", &weights_object, &h, &w, &start, &goal))
    {
        return NULL;
    }

    float *weights = (float *)weights_object->data;
    int *paths = (int*) malloc(w*h*sizeof(int));

    int path_length = run_pathfind(weights, paths, w, h, start, goal);
    
    PyObject *return_val;
    if (path_length >= 0)
    {
        npy_intp dims[2] = {path_length, 2};
        PyArrayObject *path = (PyArrayObject*) PyArray_SimpleNew(2, dims, NPY_INT32);
        npy_int32 *xptr, *yptr;

        int idx = goal;

        for (npy_intp i = dims[0] - 1; i >= 0; --i)
        {
            xptr = (npy_int32*) (path->data + i * path->strides[0]);
            yptr = (npy_int32*) (path->data + i * path->strides[0] + path->strides[1]);

            *xptr = idx / w;
            *yptr = idx % w;

            idx = paths[idx];
        }
        return_val = PyArray_Return(path);
    }
    else
    {
        return_val = Py_BuildValue("");
    }

    free(paths);

    return return_val;
}

typedef struct BSTNode {
    int key;
    struct BSTNode *left;
    struct BSTNode *right;
} BSTNode;

typedef struct BSTContainer {
    BSTNode *root;
} BSTContainer;
 
static BSTNode* bst_create(int key)
{    
    BSTNode* node = (BSTNode*) malloc(sizeof(BSTNode));
    node->key = key;
    node->left = NULL;
    node->right = NULL;
    return node;
}
 
static BSTNode* bst_add(BSTNode* root, int key)
{
    if (!root)
    {
        root = bst_create(key);
        return root;
    }
    else
    {
        BSTNode* node = bst_create(key);
        BSTNode* temp = root;
        while (temp)
        {
            if (!temp->left  && !temp->right)
            {
                if (temp->key > key)
                {
                    temp->left = node;
                    break;
                }
                else
                {
                    temp->right = node;
                    break;
                }
            }
            else
            {
                if (temp->key > key)
                {
                    if (!temp->left)
                    {
                        temp->left = node;
                        break;
                    }
                    temp = temp->left;
                }
                else
                {
                    if (!temp->right)
                    {
                        temp->right = node;
                        break;
                    }
                    temp = temp->right;
                }
            }
        }
    }
    return root;
}
 
static int bst_contains(BSTNode* root, int key)
{
    if (!root) return 0;
    if (root->key == key)
    {
        return 1;
    }
    else if (root->key > key)
    {
        return bst_contains(root->left, key);
    }
    else
    {
        return bst_contains(root->right, key);
    }
}
 
static void bst_delete(BSTNode* root)
{
    if (!root) return;
    bst_delete(root->left);
    bst_delete(root->right);
    free(root);
}

typedef struct KeyContainer
{
    int* keys;
} KeyContainer;

static void bst_collect_keys(BSTNode* root, KeyContainer *c)
{
    if (!root) return;

    sb_push(c->keys, root->key);
    bst_collect_keys(root->left, c);
    bst_collect_keys(root->right, c);
}

static int flood_fill_overlord(uint8_t *heights, uint8_t *overlord_spots, int grid_width, int grid_height, int x, int y, uint8_t target_height, uint8_t replacement, BSTContainer* bst_cont)
{
    int key = y*grid_width + x;
    
    if (bst_contains(bst_cont->root, key) == 1) return 1;

    bst_cont->root = bst_add(bst_cont->root, key);

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
    overlord_spots[key] = replacement;

    if (y > 0)
    {
        result &= flood_fill_overlord(heights, overlord_spots, grid_width, grid_height, x, y - 1, target_height, replacement, bst_cont);
    }
    if (x > 0)
    {
        result &= flood_fill_overlord(heights, overlord_spots, grid_width, grid_height, x - 1, y, target_height, replacement, bst_cont);
    }
    if (y < grid_height - 1)
    {
        result &= flood_fill_overlord(heights, overlord_spots, grid_width, grid_height, x, y + 1, target_height, replacement, bst_cont);
    }
    if (x < grid_width - 1)
    {
        result &= flood_fill_overlord(heights, overlord_spots, grid_width, grid_height, x + 1, y, target_height, replacement, bst_cont);
    }
    return result;
}

static inline float euclidean_distance(int x0, int y0, int x1, int y1)
{
    return sqrtf((float)((x0 - x1)*(x0 - x1) + (y0 - y1)*(y0 - y1)));
}


typedef struct FloatLine {
    float start[2];
    float end[2];
} FloatLine;

typedef struct IntLine {
    int start[2];
    int end[2];
} IntLine;

typedef struct Choke {
    FloatLine main_line;
    IntLine* lines;
    int* side1;
    int* side2;
    int* pixels;
    float min_length;
    int valid;
} Choke;

typedef struct ChokeLines {
    IntLine* lines;
} ChokeLines;

typedef struct ChokeList {
    Choke* chokes;
} ChokeList;

static int* get_nodes_within_distance(float* weights, int w, int h, int x, int y, float max_distance)
{
    PriorityQueue *nodes_to_visit = queue_create(w*h);

    int start = w*y + x;
    Node start_node = { start, 0.0f, 1 };
    float *costs = (float*) malloc(w*h*sizeof(float));

    for (int i = 0; i < w*h; ++i)
    {
        costs[i] = HUGE_VALF;
        nodes_to_visit->index_map[i] = -1;
    }
    
    costs[start] = 0;

    queue_push_or_update(nodes_to_visit, start_node);

    int nbrs[8];

    int *nodes_within_reach = NULL;

    while (nodes_to_visit->size > 0)
    {
        Node cur = queue_pop(nodes_to_visit);
        sb_push(nodes_within_reach, cur.idx);

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
                    
                    if (costs[nbrs[i]] < max_distance)
                    {
                        Node new_node = { nbrs[i], new_cost, cur.path_length + 1};
                        queue_push_or_update(nodes_to_visit, new_node);
                    }
                }    
            }
        }
    }
    
    free(costs);
    queue_delete(nodes_to_visit);

    return nodes_within_reach;
}

static void choke_list_delete(ChokeList* choke_list)
{
    for(int i = 0; i < sb_count(choke_list->chokes); ++i)
    {
        Choke choke = choke_list->chokes[i];
        sb_free(choke.lines);
        sb_free(choke.side1);
        sb_free(choke.side2);
        sb_free(choke.pixels);
    }
    sb_free(choke_list->chokes);
    free(choke_list);
}

static Choke choke_create_based_on_line(IntLine line)
{
    Choke choke = { 0 };
    choke.valid = 1;
    choke.main_line.start[0] = (float)line.start[0];
    choke.main_line.start[1] = (float)line.start[1];
    choke.main_line.end[0] = (float)line.end[0];
    choke.main_line.end[1] = (float)line.end[1];

    sb_push(choke.lines, line);

    sb_push(choke.side1, line.start[0]);
    sb_push(choke.side1, line.start[1]);

    sb_push(choke.side2, line.end[0]);
    sb_push(choke.side2, line.end[1]);

    choke.min_length = euclidean_distance(line.start[0], line.start[1], line.end[0], line.end[1]);

    return choke;
}

static void choke_add_line(Choke* choke, IntLine line)
{
    sb_push(choke->lines, line);

    int side1_contains_start = 0;
    for(int i = 0; i < sb_count(choke->side1) / 2; ++i)
    {
        if (choke->side1[2*i] == line.start[0] && choke->side1[2*i + 1] == line.start[1])
        {
            side1_contains_start = 1;
            break;
        }
    }
    if (side1_contains_start == 0)
    {
        sb_push(choke->side1, line.start[0]);
        sb_push(choke->side1, line.start[1]);
    }

    int side2_contains_end = 0;
    for(int i = 0; i < sb_count(choke->side2) / 2; ++i)
    {
        if (choke->side2[2*i] == line.end[0] && choke->side2[2*i + 1] == line.end[1])
        {
            side2_contains_end = 1;
            break;
        }
    }
    if (side2_contains_end == 0)
    {
        sb_push(choke->side2, line.end[0]);
        sb_push(choke->side2, line.end[1]);
    }
}

static void chokes_solve(uint8_t *border_points, float* border_weights, uint8_t *walkable, ChokeLines* choke_lines, int w, int h, int x, int y, int x_start, int y_start, int x_end, int y_end)
{
    float choke_distance = 13.0f;
    float choke_border_distance = 30.0f;

    if (border_points[w*y + x] == 1)
    {
        int* reachable_borders = get_nodes_within_distance(border_weights, w, h, x, y, choke_border_distance);

        int xmin = x;
        int xmax = min(x + (int)choke_distance, x_end);
        int ymin = max(y - (int)choke_distance, y_start);
        int ymax = min(y + (int)choke_distance, y_end);

        for (int ynew = ymin; ynew < ymax; ++ynew)
        {
            for (int xnew = xmin; xnew < xmax; ++xnew)
            {
                if (border_points[w*ynew + xnew] == 0) continue;

                float flight_distance = euclidean_distance(x, y, xnew, ynew);

                if (flight_distance > choke_distance || flight_distance < 2.0f) continue;
                
                int found = 0;
                for (int i = 0; i < sb_count(reachable_borders); ++i)
                {
                    if (reachable_borders[i] == w*ynew + xnew)
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
                    int draw_x = x + (int)unit_vector[0]*i;
                    int draw_y = y + (int)unit_vector[1]*i;

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
                    sb_push(choke_lines->lines, line);
                }

            }
        }
        sb_free(reachable_borders);
    }
}

static void choke_remove_excess_lines(Choke* choke)
{
    float *distances = NULL;
    float min_distance = HUGE_VALF;

    for(int i = 0; i < sb_count(choke->lines); ++i)
    {
        IntLine line = choke->lines[i];
        float d = euclidean_distance(line.start[0], line.start[1], line.end[0], line.end[1]);
        sb_push(distances, d);
        if (d < min_distance)
        {
            min_distance = d;
        }
    }

    IntLine* new_lines = NULL;

    for(int i = sb_count(choke->lines) - 1; i >= 0; --i)
    {
        if (distances[i] <= min_distance + 2.5f)
        {
            sb_push(new_lines, choke->lines[i]);
        }
    }

    sb_free(distances);
    sb_free(choke->lines);
    choke->lines = new_lines;
    choke->min_length = min_distance;
}

static void choke_calc_final_line(Choke* choke)
{
    float xsum = 0;
    float ysum = 0;

    int side1_count = sb_count(choke->side1) / 2;
    for(int i = 0; i < side1_count; ++i)
    {
        xsum += choke->side1[2*i];
        ysum += choke->side1[2*i + 1];
    }

    float point1[2] = { xsum / side1_count, ysum / side1_count };

    xsum = 0;
    ysum = 0;

    int side2_count = sb_count(choke->side2) / 2;
    for(int i = 0; i < side2_count; ++i)
    {
        xsum += choke->side2[2*i];
        ysum += choke->side2[2*i + 1];
    }

    float point2[2] = { xsum / side2_count, ysum / side2_count };

    choke->main_line.start[0] = point1[0];
    choke->main_line.start[1] = point1[1];
    choke->main_line.end[0] = point2[0];
    choke->main_line.end[1] = point2[1];
}

static void choke_set_pixels(Choke* choke)
{
    for (int l = 0; l < sb_count(choke->lines); ++l)
    {
        IntLine line = choke->lines[l];
        float flight_distance = euclidean_distance(line.start[0], line.start[1], line.end[0], line.end[1]);
        int dots = (int)flight_distance;
        float unit_vector[2] = { (line.end[0] - line.start[0]) / flight_distance, (line.end[1] - line.start[1]) / flight_distance };
        
        for (int i = 1; i < dots * 2; ++i)
        {
            int draw_x = (int)(line.start[0] + unit_vector[0]* i * 0.5f);
            int draw_y = (int)(line.start[1] + unit_vector[1]* i * 0.5f);

            if ((draw_x == line.start[0] && draw_y == line.start[1]) || (draw_x == line.end[0] && draw_y == line.end[1]))
            {
                continue;
            }

            int contained = 0;

            for(int j = 0; j < sb_count(choke->pixels) / 2; j++)
            {
                if (choke->pixels[2*j] == draw_x && choke->pixels[2*j + 1] == draw_y)
                {
                    contained = 1;
                    break;
                }
            }

            if(!contained)
            {
                sb_push(choke->pixels, draw_x);
                sb_push(choke->pixels, draw_y);
            }
        }
    }
}

static ChokeList* chokes_group(ChokeLines* choke_lines)
{
    ChokeList *list = (ChokeList*)malloc(sizeof(ChokeList));
    list->chokes = NULL;

    int line_count = sb_count(choke_lines->lines);
    uint8_t *used_indices = calloc(line_count, sizeof(uint8_t));
    for (int i = 0; i < line_count; ++i)
    {
        if (used_indices[i]) continue;

        used_indices[i] = 1;

        Choke current_choke = choke_create_based_on_line(choke_lines->lines[i]);

        int last_line_count = 0;
        int current_line_count = sb_count(current_choke.lines);
        
        while (last_line_count < current_line_count)
        {
            for (int j = i + 1; j < line_count; ++j)
            {
                if (used_indices[j]) continue;

                IntLine check_line = choke_lines->lines[j];
                for (int k = 0; k < sb_count(current_choke.side1) / 2; ++k)
                {
                    int point_x = current_choke.side1[2*k];
                    int point_y = current_choke.side1[2*k + 1];

                    int added = 0;

                    if (distance_heuristic(check_line.start[0], check_line.start[1], point_x, point_y, 1) <= SQRT2 + 0.05f)
                    {
                        for (int l = 0; l < sb_count(current_choke.side2) / 2; ++l)
                        {
                            int point2_x = current_choke.side2[2*l];
                            int point2_y = current_choke.side2[2*l + 1];

                            if (distance_heuristic(check_line.end[0], check_line.end[1], point2_x, point2_y, 1) <= SQRT2 + 0.05f)
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
                        for (int l = 0; l < sb_count(current_choke.side2) / 2; ++l)
                        {
                            int point2_x = current_choke.side2[2*l];
                            int point2_y = current_choke.side2[2*l + 1];

                            if (distance_heuristic(check_line.start[0], check_line.start[1], point2_x, point2_y, 1) <= SQRT2)
                            {
                                used_indices[j] = 1;

                                if (distance_heuristic(check_line.end[0], check_line.end[1], point_x, point_y, 1) > 0 || distance_heuristic(check_line.start[0], check_line.start[1], point2_x, point2_y, 1) > 0)
                                {
                                    IntLine line_to_add = { { check_line.end[0], check_line.end[1] }, { check_line.start[0], check_line.start[1] }};
                                    choke_add_line(&current_choke, line_to_add);
                                    added = 1;
                                    break;
                                }
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
            current_line_count = sb_count(current_choke.lines);
        }
        sb_push(list->chokes, current_choke);
    }

    free(used_indices);

    for (int i = sb_count(list->chokes) - 1; i >= 0; --i)
    {
        Choke current_choke = list->chokes[i];

        choke_remove_excess_lines(&list->chokes[i]);
        choke_calc_final_line(&list->chokes[i]);
        if (sb_count(list->chokes[i].lines) < 4)
        {
            list->chokes[i].valid = 0;
        }
        else
        {
            choke_set_pixels(&list->chokes[i]);
        }
    }
    
    return list;
}

static PyObject* choke_list_to_pyobject(ChokeList *list)
{
    int choke_count = sb_count(list->chokes);

    int valid_choke_count = 0;

    for(int i = 0; i < choke_count; ++i)
    {
        Choke choke = list->chokes[i];
        if (!choke.valid) continue;

        ++valid_choke_count;
    }

    PyObject* return_list = PyList_New(valid_choke_count);
    
    int valid_index = 0;

    for(int i = 0; i < choke_count; ++i)
    {
        Choke choke = list->chokes[i];
        if (!choke.valid) continue;

        PyObject *py_choke = PyTuple_New(6);

        PyObject *py_main_line = PyTuple_New(2);
        PyObject *py_lines = PyList_New(sb_count(choke.lines));
        PyObject *py_side1 = PyList_New(sb_count(choke.side1) / 2);
        PyObject *py_side2 = PyList_New(sb_count(choke.side2) / 2);
        PyObject *py_pixels = PyList_New(sb_count(choke.pixels) / 2);
        PyObject *py_min_length = PyFloat_FromDouble((double)choke.min_length);
        
        PyObject* main_line_start = PyTuple_New(2);
        PyTuple_SetItem(main_line_start, 0, PyFloat_FromDouble((double)choke.main_line.start[1]));
        PyTuple_SetItem(main_line_start, 1, PyFloat_FromDouble((double)choke.main_line.start[0]));

        PyObject* main_line_end = PyTuple_New(2);
        PyTuple_SetItem(main_line_end, 0, PyFloat_FromDouble((double)choke.main_line.end[1]));
        PyTuple_SetItem(main_line_end, 1, PyFloat_FromDouble((double)choke.main_line.end[0]));

        PyTuple_SetItem(py_main_line, 0, main_line_start);
        PyTuple_SetItem(py_main_line, 1, main_line_end);

        for (int j = 0; j < sb_count(choke.lines); ++j)
        {
            PyObject* cur = PyTuple_New(2);
            
            PyObject* first_tuple = PyTuple_New(2);
            PyTuple_SetItem(first_tuple, 0, PyLong_FromLong(choke.lines[j].start[1]));
            PyTuple_SetItem(first_tuple, 1, PyLong_FromLong(choke.lines[j].start[0]));
            
            PyObject* second_tuple = PyTuple_New(2);
            PyTuple_SetItem(second_tuple, 0, PyLong_FromLong(choke.lines[j].end[1]));
            PyTuple_SetItem(second_tuple, 1, PyLong_FromLong(choke.lines[j].end[0]));
            
            PyTuple_SetItem(cur, 0, first_tuple);
            PyTuple_SetItem(cur, 1, second_tuple);

            PyList_SetItem(py_lines, j, cur);
        }

        for (int j = 0; j < sb_count(choke.side1) / 2; ++j)
        {
            PyObject *cur = PyTuple_New(2);
            PyTuple_SetItem(cur, 0, PyLong_FromLong(choke.side1[2*j + 1]));
            PyTuple_SetItem(cur, 1, PyLong_FromLong(choke.side1[2*j]));

            PyList_SetItem(py_side1, j, cur);
        }
        
        for (int j = 0; j < sb_count(choke.side2) / 2; ++j)
        {
            PyObject *cur = PyTuple_New(2);
            PyTuple_SetItem(cur, 0, PyLong_FromLong(choke.side2[2*j + 1]));
            PyTuple_SetItem(cur, 1, PyLong_FromLong(choke.side2[2*j]));

            PyList_SetItem(py_side2, j, cur);
        }

        for (int j = 0; j < sb_count(choke.pixels) / 2; ++j)
        {
            PyObject *cur = PyTuple_New(2);
            PyTuple_SetItem(cur, 0, PyLong_FromLong(choke.pixels[2*j + 1]));
            PyTuple_SetItem(cur, 1, PyLong_FromLong(choke.pixels[2*j]));

            PyList_SetItem(py_pixels, j, cur);
        }

        PyTuple_SetItem(py_choke, 0, py_main_line);
        PyTuple_SetItem(py_choke, 1, py_lines);
        PyTuple_SetItem(py_choke, 2, py_side1);
        PyTuple_SetItem(py_choke, 3, py_side2);
        PyTuple_SetItem(py_choke, 4, py_pixels);
        PyTuple_SetItem(py_choke, 5, py_min_length);

        PyList_SetItem(return_list, valid_index, py_choke);
        ++valid_index;
    }

    return return_list;
}

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

    uint8_t *climbable_points = (uint8_t *)calloc(w*h, sizeof(uint8_t));
    uint8_t *overlord_spots = (uint8_t *)calloc(w*h, sizeof(uint8_t));
    uint8_t *border_points = (uint8_t *)calloc(w*h, sizeof(uint8_t));
    float *choke_weights = (float *)malloc(w*h*sizeof(float));

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
                uint8_t h0 = heights[w*(y + 1) + x];
                uint8_t h1 = heights[w*(y - 1) + x];
                uint8_t hxy = heights[w*y + x];

                if ((hxy >= h0 + LEVEL_DIFFERENCE && h0 > 0) || (hxy >= h1 + LEVEL_DIFFERENCE && h1 > 0))
                {
                    overlord_spots[w*y + x] = 1;
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
                    border_points[w*y + x] = 1;
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
                            climbable_points[w*y1 + x1] = 1;
                        }
                        else if ((h0 == h1 && h0 == h3 && h0 == h2 + LEVEL_DIFFERENCE) || (h0 == h2 && h0 == h3 && h1 == h2 + LEVEL_DIFFERENCE))
                        {
                            climbable_points[w*y1 + x1] = 1;
                        }
                    }
                    else
                    {
                        if ((h1 == h2 && h1 == h3 && h1 == h0 + LEVEL_DIFFERENCE) || (h0 == h1 && h0 == h2 && h3 == h0 + LEVEL_DIFFERENCE))
                        {
                            climbable_points[w*y1 + x1] = 1;
                        }
                        else if((h0 == h1 && h0 == h2 && h0 == h3 + LEVEL_DIFFERENCE) || (h1 == h2 && h1 == h3 && h0 == h3 + LEVEL_DIFFERENCE))
                        {
                            climbable_points[w*y1 + x1] = 1;
                        }
                    }
                }
                else
                {
                    if (xdir != 0)
                    {
                        if (h0 == h2 && h1 == h3 && h0 + LEVEL_DIFFERENCE == h1)
                        {
                            climbable_points[w*y1 + x1] = 1;
                        }
                        else if(h0 == h2 && h1 == h3 && h0 == h1 + LEVEL_DIFFERENCE)
                        {
                            climbable_points[w*y1 + x1] = 1;
                        }
                    }   
                    else if(ydir != 0)
                    {
                        if (h0 == h1 && h2 == h3 && h0 + LEVEL_DIFFERENCE == h2)
                        {
                            climbable_points[w*y1 + x1] = 1;
                        }
                        else if (h0 == h1 && h2 == h3 && h0 == h2 + LEVEL_DIFFERENCE)
                        {
                            climbable_points[w*y1 + x1] = 1;
                        }
                    }    
                }
            }
        }
    }

    BSTNode *handled_overlord_spots = NULL;
    float* overlord_spot_arr = NULL;

    npy_intp climber_dims[2] = {h, w};
    PyArrayObject *climber_mat = (PyArrayObject*) PyArray_ZEROS(2, climber_dims, NPY_FLOAT32, 0);

    ChokeLines choke_lines = { NULL };

    for (int y = 1; y < h - 1; ++y)
    {
        for (int x = 1; x < w - 1; ++x)
        {
            if (climbable_points[w*y + x] == 1
                && (climbable_points[w*y + x + 1] == 1
                    || climbable_points[w*y + x - 1] == 1
                    || climbable_points[w*(y + 1) + x] == 1
                    || climbable_points[w*(y - 1) + x] == 1))
            {
                npy_float32 *ptr = (npy_float32*) (climber_mat->data + y * climber_mat->strides[0] + x * climber_mat->strides[1]);
                *ptr = 1.0f;
            }

            int key = w*y + x;

            if (bst_contains(handled_overlord_spots, key) == 0 && overlord_spots[key] == 1)
            {
                uint8_t target_height = heights[key];
                BSTContainer current_set = { NULL };
                if (flood_fill_overlord(heights, overlord_spots, w, h, x, y, target_height, 1, &current_set) == 1)
                {
                    float spot[2] = { 0.0f, 0.0f };
                    KeyContainer c = { NULL };
                    bst_collect_keys(current_set.root, &c);

                    for(int i = 0; i < sb_count(c.keys); ++i)
                    {
                        handled_overlord_spots = bst_add(handled_overlord_spots, c.keys[i]);
                        int cx = c.keys[i] % w;
                        int cy = c.keys[i] / w;
                        spot[0] += cy;
                        spot[1] += cx;
                    }

                    spot[0] = spot[0] / (float)sb_count(c.keys);
                    spot[1] = spot[1] / (float)sb_count(c.keys);
                    sb_push(overlord_spot_arr, spot[0]);
                    sb_push(overlord_spot_arr, spot[1]);
                    sb_free(c.keys);
                }
                else
                {
                    bst_delete(current_set.root);
                    current_set.root = NULL;
                    flood_fill_overlord(heights, overlord_spots, w, h, x, y, target_height, 0, &current_set);
                }

                if(current_set.root) bst_delete(current_set.root);

            }

            chokes_solve(border_points, choke_weights, walkable, &choke_lines, w, h, x, y, x_start, y_start, x_end, y_end);
        }
    }

    ChokeList *choke_list = chokes_group(&choke_lines);

    npy_intp overlord_dims[2] = {sb_count(overlord_spot_arr) / 2, 2};

    PyArrayObject *overlord_mat = (PyArrayObject*) PyArray_SimpleNew(2, overlord_dims, NPY_FLOAT32);

    npy_float32 *overlord_mat_data = (npy_float32*)overlord_mat->data;
    for(int i = 0; i < sb_count(overlord_spot_arr); ++i)
    {
        overlord_mat_data[i] = overlord_spot_arr[i];
    }
    PyObject* return_chokes = choke_list_to_pyobject(choke_list);

    sb_free(choke_lines.lines);
    choke_list_delete(choke_list);
    sb_free(overlord_spot_arr);
    bst_delete(handled_overlord_spots);
    free(climbable_points);
    free(overlord_spots);
    free(border_points);
    free(choke_weights);

    PyObject *return_tuple = PyTuple_New(3);
    PyObject *return_climber = PyArray_Return(climber_mat);
    PyObject *return_overlords = PyArray_Return(overlord_mat);

    PyTuple_SetItem(return_tuple, 0, return_climber);
    PyTuple_SetItem(return_tuple, 1, return_overlords);
    PyTuple_SetItem(return_tuple, 2, return_chokes);
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
  import_array();
  return PyModule_Create(&cext_module);
}