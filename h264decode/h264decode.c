#include <Python.h>
#include <libavcodec/avcodec.h>

AVCodec *h264decoder_h264Codec;

static PyMethodDef h264decode_methods[] = {
	{NULL, NULL, 0, NULL}
};

extern PyTypeObject h264decode_DecoderType;
extern PyTypeObject h264decode_YUVFrameType;

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC inith264decode(void)
{
    avcodec_register_all();
    h264decoder_h264Codec = avcodec_find_decoder(CODEC_ID_H264);
	if (!h264decoder_h264Codec) {
		PyErr_SetString(PyExc_SystemError, "No H.264 codec found in this installation of libavcodec");
		return;
	}

	if (PyType_Ready(&h264decode_DecoderType) < 0)
		return;

	if (PyType_Ready(&h264decode_YUVFrameType) < 0)
		return;

	PyObject *module = Py_InitModule3("h264decode", h264decode_methods,
			"A simple wrapper around libavcodec to decode complete H.264 packets to YUV420p frames");
	if (!module)
		return;

    Py_INCREF(&h264decode_DecoderType);
	PyModule_AddObject(module, "Decoder", (PyObject *)&h264decode_DecoderType);

    Py_INCREF(&h264decode_YUVFrameType);
	PyModule_AddObject(module, "YUVFrame", (PyObject *)&h264decode_YUVFrameType);
}
