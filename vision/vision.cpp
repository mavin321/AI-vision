#include "vision.h"

#include <opencv2/imgproc.hpp>

namespace vision_ext {
cv::Mat preprocess_frame(const cv::Mat &frame) {
  cv::Mat gray, blurred, edges, merged;
  cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);
  cv::GaussianBlur(gray, blurred, cv::Size(3, 3), 0);
  cv::Canny(blurred, edges, 30, 90);
  cv::cvtColor(edges, merged, cv::COLOR_GRAY2BGR);
  return merged;
}
}  // namespace vision_ext
