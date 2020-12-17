#define PY_SSIZE_T_CLEAN
#include <Python.h> // includes stdlib.h
#include <numpy/arrayobject.h>
#include <math.h>
#include "stretchy_buffer.h"

#define LEVEL_DIFFERENCE 16

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
    float minimum = HUGE_VAL;
    for (int i = 0; i < length; ++i)
    {
        minimum = min(arr[i], minimum);
    }
    return minimum;
}

static inline float distance_heuristic(int x0, int y0, int x1, int y1, float baseline)
{
    return baseline*(max(abs(x0 - x1), abs(y0 - y1)) + 0.41421f * min(abs(x0 - x1), abs(y0 - y1)));
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
    float weight_baseline = find_min(weights, w*h);

    int *paths = (int*) malloc(w*h*sizeof(int));
    
    int path_length = -1;

    PriorityQueue *nodes_to_visit = queue_create(w*h);

    Node start_node = { start, 0.0f, 1 };
    float *costs = (float*) malloc(w*h*sizeof(float));

    for (int i = 0; i < w*h; ++i)
    {
        costs[i] = HUGE_VAL;
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
                    new_cost += weights[nbrs[i]] * 1.4142f;
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

    free(costs);
    free(paths);
    queue_delete(nodes_to_visit);

    return return_val;
}

typedef struct BSTNode {
    int key;
    struct BSTNode *left;
    struct BSTNode *right;
} BSTNode;

typedef struct BSTContainer {
    BSTNode *root;
    int* keys;
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
        return target_height >= heights[key] + LEVEL_DIFFERENCE;
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

static PyObject* get_map_data(PyObject *self, PyObject *args)
{
    PyArrayObject* pathable_object;
    PyArrayObject* heights_object;
    int h, w;
    
    if (!PyArg_ParseTuple(args, "OOii", &pathable_object, &heights_object, &h, &w))
    {
        return NULL;
    }

    uint8_t *pathable = (uint8_t *)pathable_object->data;
    uint8_t *heights = (uint8_t *)heights_object->data;

    uint8_t *climbable_points = (uint8_t *)calloc(w*h, sizeof(uint8_t));
    uint8_t *overlord_spots = (uint8_t *)calloc(w*h, sizeof(uint8_t));

    int dirs[8] = { -1, -1, 1, -1, 1, 0, 0, 1 };

    for (int y = 2; y < h - 2; ++y)
    {
        for (int x = 2; x < w - 2; ++x)
        {
            if (pathable[w*y + x] == 0)
            {
                uint8_t h0 = heights[w*(y + 1) + x];
                uint8_t h1 = heights[w*(y - 1) + x];
                uint8_t hxy = heights[w*y + x];

                if ((hxy >= h0 + LEVEL_DIFFERENCE && h0 > 0) || (hxy >= h1 + LEVEL_DIFFERENCE && h1 > 0))
                {
                    overlord_spots[w*y + x] = 1;
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

                if (pathable[w*y1 + x1] == 1 || pathable[w*y2 + x2] == 0) continue;

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
                BSTContainer current_set = { NULL, NULL };
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
        }
    }

    npy_intp overlord_dims[2] = {sb_count(overlord_spot_arr) / 2, 2};

    PyArrayObject *overlord_mat = (PyArrayObject*) PyArray_SimpleNew(2, overlord_dims, NPY_FLOAT32);

    float *overlord_mat_data = (float*)overlord_mat->data;
    for(int i = 0; i < sb_count(overlord_spot_arr); ++i)
    {
        overlord_mat_data[i] = overlord_spot_arr[i];
    }

    sb_free(overlord_spot_arr);
    bst_delete(handled_overlord_spots);
    free(climbable_points);
    free(overlord_spots);

    PyObject *return_tuple = PyTuple_New(2);
    PyObject *return_climber = PyArray_Return(climber_mat);
    PyObject *return_overlords = PyArray_Return(overlord_mat);

    PyTuple_SetItem(return_tuple, 0, return_climber);
    PyTuple_SetItem(return_tuple, 1, return_overlords);

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
