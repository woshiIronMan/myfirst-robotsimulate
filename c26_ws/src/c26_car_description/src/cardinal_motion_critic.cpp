#include <cmath>

#include "dwb_core/exceptions.hpp"
#include "dwb_core/trajectory_critic.hpp"
#include "pluginlib/class_list_macros.hpp"

namespace c26_car_description
{
class CardinalMotionCritic : public dwb_core::TrajectoryCritic
{
public:
  double scoreTrajectory(const dwb_msgs::msg::Trajectory2D & trajectory) override
  {
    constexpr double zero = 1e-6;
    const auto & velocity = trajectory.velocity;
    if (std::abs(velocity.y) <= zero) {
      return 0.0;
    }
    if (std::abs(velocity.x) > zero || std::abs(velocity.theta) > zero) {
      throw dwb_core::IllegalTrajectoryException(name_, "Strafing must be straight and purely lateral");
    }
    // Prefer steering along the route when a longitudinal trajectory scores similarly.
    return 1.0;
  }
};
}  // namespace c26_car_description

PLUGINLIB_EXPORT_CLASS(c26_car_description::CardinalMotionCritic, dwb_core::TrajectoryCritic)
