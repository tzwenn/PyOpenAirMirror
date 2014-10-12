#include <Python.h>
#include <libavcodec/avcodec.h>
#include <libavutil/mem.h>

#if LIBAVCODEC_VERSION_INT < AV_VERSION_INT(55,28,1)
#define av_frame_alloc  avcodec_alloc_frame
#endif

extern AVCodec *h264decoder_h264Codec; // defined in h264decode.c
extern PyObject *h264decode_YUVFrame_from_AVPicture(AVFrame *picture);

typedef struct {
	PyObject_HEAD

	AVCodecContext *codec_context;
	uint8_t *avccData;
	AVFrame *picture;
	AVPacket packet;
} h264decode_Decoder;

static PyObject *Decoder_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	h264decode_Decoder *self;
	self = (h264decode_Decoder *)type->tp_alloc(type, 0);
	if (self) {
		self->codec_context = NULL;
		self->avccData = NULL;
		self->picture = NULL;
	}

	return (PyObject *)self;
}

static void Decoder_dealloc(h264decode_Decoder *self)
{
	if (self->codec_context) {
	    avcodec_close(self->codec_context);
	    av_free(self->codec_context);
	}
	if (self->picture) {
		av_free(self->picture);
	}
	if (self->avccData) {
		free(self->avccData);
	}
    self->ob_type->tp_free((PyObject*)self);
}

static int Decoder_init(h264decode_Decoder *self, PyObject *args, PyObject *kwds)
{
	int len;
	char *avccData;
	if (!PyArg_ParseTuple(args, "s#", &avccData, &len))
		return -1;

	av_init_packet(&self->packet);

	self->picture = av_frame_alloc();
	if (!self->picture) {
		PyErr_SetString(PyExc_RuntimeError, "Cannot allocate output frame buffer");
		return -1;
	}

    self->codec_context = avcodec_alloc_context3(h264decoder_h264Codec);
	if (!self->codec_context) {
		PyErr_SetString(PyExc_RuntimeError, "Cannot allocate H.264 codec context");
		goto failPostFrame;
		return -1;
	}

	self->avccData = (uint8_t *)calloc(len + FF_INPUT_BUFFER_PADDING_SIZE, sizeof(uint8_t));
	if (!self->avccData) {
		// FIXME: Wasn't there a proper way to report failed mallocs? I just forgot atm
		PyErr_SetString(PyExc_RuntimeError, "Cannot allocate memory for codec extradata");
		goto failPostCodec;
	}
	memcpy(self->avccData, avccData, len);
	self->codec_context->extradata = self->avccData;
	self->codec_context->extradata_size = len;

	/*   if(h264decoder_h264Codec->capabilities&CODEC_CAP_TRUNCATED)
        self->codec_context->flags|= CODEC_FLAG_TRUNCATED; */

	if (avcodec_open2(self->codec_context, h264decoder_h264Codec, NULL) < 0) {
		PyErr_SetString(PyExc_RuntimeError, "Cannot open H.264 codec with set avcC");
		goto failPostData;
	}
	return 0;

failPostData:
	free(self->avccData);

failPostCodec:
	av_free(self->codec_context);

failPostFrame:
	av_free(self->picture);
	return -1;
}

static PyObject *Decoder_width(h264decode_Decoder *self)
{
	return PyInt_FromLong(self->codec_context->width);
}

static PyObject *Decoder_height(h264decode_Decoder *self)
{
	return PyInt_FromLong(self->codec_context->height);
}

static PyObject *Decoder_decodeFrame(h264decode_Decoder *self, PyObject *args)
{
	char *unpaddedData;
	if (!PyArg_ParseTuple(args, "s#", &unpaddedData, &self->packet.size))
		return NULL;

	if (!self->packet.size)
		return Py_BuildValue("");

	uint8_t *paddedData = calloc(self->packet.size + FF_INPUT_BUFFER_PADDING_SIZE, 1);
	if (!paddedData) {
		PyErr_SetString(PyExc_RuntimeError, "Cannot allocate memory for padded buffer");
		return NULL;
	}
	memcpy(paddedData, unpaddedData, self->packet.size);
	self->packet.data = paddedData;

	int got_picture;
	avcodec_decode_video2(self->codec_context, self->picture, &got_picture, &self->packet);

	PyObject *res = NULL;
	if (got_picture) {
		res = h264decode_YUVFrame_from_AVPicture(self->picture);
	}
	free(paddedData);
	return res ? res : Py_BuildValue("");
}

static PyMethodDef Decoder_methods[] = {
	{"width", (PyCFunction)Decoder_width, METH_NOARGS, "Return the width of the output frames"},
	{"height", (PyCFunction)Decoder_height, METH_NOARGS, "Return the height of the output frames"},
	{"decodeFrame", (PyCFunction)Decoder_decodeFrame, METH_VARARGS, "Decode a frame from the passed blob (which is expected to be a complete, single packet)"},
	{NULL, NULL, 0, NULL}
};

PyTypeObject h264decode_DecoderType = {
	PyObject_HEAD_INIT(NULL)
	0,                         /*ob_size*/
	"h264decode.Decoder",      /*tp_name*/
	sizeof(h264decode_Decoder), /*tp_basicsize*/
	0,                         /*tp_itemsize*/
	(destructor)Decoder_dealloc,  /*tp_dealloc*/
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
	0,                         /*tp_str*/
	0,                         /*tp_getattro*/
	0,                         /*tp_setattro*/
	0,                         /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT,        /*tp_flags*/ // No Py_TPFLAGS_BASETYPE
	"Active decoding context", /* tp_doc */
	0,		                   /* tp_traverse */
	0,		                   /* tp_clear */
	0,		                   /* tp_richcompare */
	0,		                   /* tp_weaklistoffset */
	0,		                   /* tp_iter */
	0,		                   /* tp_iternext */
	Decoder_methods,           /* tp_methods */
	0,                         /* tp_members */
	0,                         /* tp_getset */
	0,                         /* tp_base */
	0,                         /* tp_dict */
	0,                         /* tp_descr_get */
	0,                         /* tp_descr_set */
	0,                         /* tp_dictoffset */
	(initproc)Decoder_init,    /* tp_init */
	0,                         /* tp_alloc */
	Decoder_new,               /* tp_new */
};

