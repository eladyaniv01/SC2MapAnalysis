#define PY_SSIZE_T_CLEAN
#include <Python.h> // includes stdlib.h
#include <numpy/arrayobject.h>
#include <math.h>

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

static inline int queue_parent(int i) 
{ 
  
    return (i - 1) / 2; 
} 
  
static inline int queue_left_child(int i) 
{ 
  
    return ((2 * i) + 1); 
} 
  
static inline int queue_right_child(int i) 
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
    while (index > 0 && nodes[queue_parent(index)].cost > nodes[index].cost)
    { 
        queue_swap(queue, queue_parent(index), index); 
        index = queue_parent(index); 
    } 
}

static void queue_down(PriorityQueue *queue, int index)
{
    int min_index = index;
    Node* nodes = queue->nodes;

    for (;;)
    {
        int l = queue_left_child(index); 
  
        if (l < queue->size && nodes[l].cost < nodes[min_index].cost) { 
            min_index = l; 
        } 
    
        int r = queue_right_child(index); 
    
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

static PyMethodDef astar_methods[] = {
    {"astar", (PyCFunction)astar, METH_VARARGS, "astar"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef astar_module = {
    PyModuleDef_HEAD_INIT,"astar", NULL, -1, astar_methods
};

PyMODINIT_FUNC PyInit_mapanalyzerext(void) {
  import_array();
  return PyModule_Create(&astar_module);
}
