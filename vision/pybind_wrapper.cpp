#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <opencv2/core.hpp>

#include "vision.h"

namespace py = pybind11;

py::array_t<uint8_t> preprocess(py::array_t<uint8_t> input) {
  py::buffer_info buf = input.request();
  if (buf.ndim != 3) {
    throw std::runtime_error("Expected HxWxC array");
  }
  const int height = static_cast<int>(buf.shape[0]);
  const int width = static_cast<int>(buf.shape[1]);
  const int channels = static_cast<int>(buf.shape[2]);

  cv::Mat frame(height, width, CV_8UC(channels), buf.ptr);
  cv::Mat output = vision_ext::preprocess_frame(frame);

  auto result = py::array_t<uint8_t>({output.rows, output.cols, output.channels()});
  py::buffer_info out_buf = result.request();
  std::memcpy(out_buf.ptr, output.data, output.total() * output.elemSize());
  return result;
}

PYBIND11_MODULE(vision, m) {
  m.doc() = "Fast preprocessing extension for Local AI Vision Keyboard";
  m.def("preprocess", &preprocess, "Preprocess frame for gesture detection");
}
