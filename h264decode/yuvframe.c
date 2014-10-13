#include <Python.h>
#include <structmember.h>
#include <libavcodec/avcodec.h>
#include <string.h>

typedef struct {
	PyObject_HEAD

	int width;
	int height;

	PyObject *y;
	PyObject *u;
	PyObject *v;
} h264decode_YUVFrame;

static PyObject *YUVFrame_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	h264decode_YUVFrame *self;
	self = (h264decode_YUVFrame *)type->tp_alloc(type, 0);
	if (self) {
		self->width = 0;
		self->height = 0;

		self->y = PyString_FromString("");
		if (!self->y) {
			Py_DECREF(self);
			return NULL;
		}
		self->u = PyString_FromString("");
		if (!self->u) {
			Py_DECREF(self);
			return NULL;
		}
		self->v = PyString_FromString("");
		if (!self->v) {
			Py_DECREF(self);
			return NULL;
		}
	}
	return (PyObject *)self;
}

static int YUVFrame_init(h264decode_YUVFrame *self, PyObject *args, PyObject *kwds)
{
	return 0;
}

static int YUVFrame_traverse(h264decode_YUVFrame *self, visitproc visit, void *arg)
{
	Py_VISIT(self->y);
	Py_VISIT(self->u);
	Py_VISIT(self->v);
	return 0;
}

static int YUVFrame_clear(h264decode_YUVFrame *self)
{
	Py_CLEAR(self->y);
	Py_CLEAR(self->u);
	Py_CLEAR(self->v);
	return 0;
}

static void YUVFrame_dealloc(h264decode_YUVFrame *self)
{
	YUVFrame_clear(self);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *YUVFrame_str(h264decode_YUVFrame *self)
{
	return PyString_FromFormat("h264decode.YUVFrame{%dx%d pixels}", self->width, self->height);
}

static PyMemberDef YUVFrame_members[] = {
    {"width", T_INT, offsetof(h264decode_YUVFrame, width), 0, "width of frame in pixels"},
    {"height", T_INT, offsetof(h264decode_YUVFrame, height), 0, "height of frame in pixels"},
    {"y", T_OBJECT_EX, offsetof(h264decode_YUVFrame, y), 0, "the raw Y data (height lines)"},
    {"u", T_OBJECT_EX, offsetof(h264decode_YUVFrame, u), 0, "the raw U data (height/2 lines)"},
    {"v", T_OBJECT_EX, offsetof(h264decode_YUVFrame, v), 0, "the raw V data (height/2 lines)"},
    {NULL}  /* Sentinel */
};

static PyMethodDef YUVFrame_methods[] = {
	{NULL, NULL, 0, NULL}
};

PyTypeObject h264decode_YUVFrameType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "h264decode.YUVFrame",    /*tp_name*/
    sizeof(h264decode_YUVFrame),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)YUVFrame_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    (reprfunc)YUVFrame_str,    /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC, /*tp_flags*/
    "A YUV420p frame as returned by x264 decoder in ffmpeg",           /* tp_doc */
    (traverseproc)YUVFrame_traverse,       /* tp_traverse */
    (inquiry)YUVFrame_clear,  /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    YUVFrame_methods,          /* tp_methods */
    YUVFrame_members,          /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)YUVFrame_init,   /* tp_init */
    0,                         /* tp_alloc */
    YUVFrame_new,              /* tp_new */
};

// Reduce linesize to provided width
static PyObject *bundleFrameData(uint8_t *dst, uint8_t *src, int linesize, int width, int height)
{
	int i;
	for (i = 0; i < height; ++i) {
		memcpy(dst + i * width, src + i * linesize, width);
	}
	return Py_BuildValue("s#", dst, width * height);
}

PyObject *h264decode_YUVFrame_from_AVPicture(AVFrame *picture)
{
	h264decode_YUVFrame *self = (h264decode_YUVFrame *)
					PyObject_CallObject((PyObject *) &h264decode_YUVFrameType, NULL);

	self->width = picture->width;
	self->height = picture->height;

	uint8_t *auxBuf = malloc(picture->height * picture->width);
	if (!auxBuf) {
		PyErr_SetString(PyExc_RuntimeError, "Cannot allocate memory for bundling frame");
		goto delSelf;
	}

	Py_CLEAR(self->y);
	self->y = bundleFrameData(auxBuf, picture->data[0], picture->linesize[0], picture->width, picture->height);
	if (!self->y) {
		goto fail;
	}
	
	Py_CLEAR(self->u);
	self->u = bundleFrameData(auxBuf, picture->data[1], picture->linesize[1], picture->width / 2, picture->height / 2);
	if (!self->u) {
		goto fail;
	}
	
	Py_CLEAR(self->v);
	self->v = bundleFrameData(auxBuf, picture->data[2], picture->linesize[2], picture->width / 2, picture->height / 2);
	if (!self->v) {
		goto fail;
	}
	free(auxBuf);
	return (PyObject  *)self;

fail:
	free(auxBuf);
delSelf:
	Py_DECREF(self);
	return NULL;
}
