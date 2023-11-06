import math
import turtle

# Constants
MIRRORS = [
    ((100, -100), (100, 100)),
    ((100, 100), (-100, 100)),
]
RAYS = [
    {'start': (0, 0), 'color': 'black'},
    {'start': (-50, 50), 'color': 'red'},
]
ANGLES = range(0, 360, 10)
ITERATIONS = 100


def setup_screen():
    """
    Set up the turtle screen for the simulation.

    Returns:
    turtle.Screen: The turtle screen object.
    """
    screen = turtle.Screen()
    screen.setup()
    screen.title("Ray Reflection Simulation")
    screen.tracer(0)
    return screen


def draw_mirrors():
    """
    Draw the mirrors on the turtle screen.
    """
    for mirror in MIRRORS:
        start, end = mirror
        turtle.penup()
        turtle.goto(start)
        turtle.pendown()
        turtle.goto(end)
        turtle.hideturtle()


def create_ray(angle, start, color):
    """
    Create a turtle object representing a ray at a given angle.

    Args:
    angle (int): The initial angle of the ray.
    start (tuple): The coordinates of the ray's starting point.
    color (str): The color of the ray.

    Returns:
    turtle.Turtle: The turtle object representing the ray.
    """
    ray = turtle.Turtle()
    ray.color(color)
    ray.speed(0)
    ray.penup()
    ray.goto(start)
    ray.left(angle)
    ray.pendown()
    return ray


def distance(point, line_start, line_end):
    """
    Calculate the distance between a point and a line defined by two points.

    Args:
    point (tuple): The coordinates of the point.
    line_start (tuple): The coordinates of the line's starting point.
    line_end (tuple): The coordinates of the line's ending point.

    Returns:
    float: The distance between the point and the line.
    """
    x, y = point
    x1, y1 = line_start
    x2, y2 = line_end
    distance = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 -
                   y2 * x1) / math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
    return distance


def reflect_ray(incident_angle, line_start, line_end):
    """
    Calculate the reflection angle based on the incident angle and mirror
    orientation.

    Args:
    incident_angle (float): The incident angle of the ray.
    line_start (tuple): The coordinates of the mirror's starting point.
    line_end (tuple): The coordinates of the mirror's ending point.

    Returns:
    float: The reflection angle.
    """
    x1, y1 = line_start
    x2, y2 = line_end
    mirror_angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    reflection_angle = 2 * mirror_angle - incident_angle
    return reflection_angle


def extend_ray(ray):
    """
    Extend the ray to simulate the reflection.

    Args:
    ray (turtle.Turtle): The turtle object representing the ray.
    """
    extension_length = 1000
    distance = 0
    angle = ray.heading()
    ray.setheading(angle-180)
    while distance <= extension_length:
        ray.pendown()
        ray.forward(10)
        ray.penup()
        ray.forward(10)
        distance += 20
    ray.setheading(angle)
    ray.forward(distance)
    ray.pendown()


def simulate_rays(rays):
    """
    Simulate the reflection of rays off mirrors.

    Args:
    rays (list): List of turtle objects representing rays.
    """
    for ray in rays:
        for mirror in MIRRORS:
            start, end = mirror
            sx, sy = start
            ex, ey = end

            intersection = distance(ray.position(), start, end)
            in_boundary = (sy < ray.ycor() < ey) or (ex < ray.xcor() < sx)

            if intersection <= 1.5 and in_boundary:
                reflection_angle = reflect_ray(ray.heading(), start, end)
                ray.setheading(reflection_angle)
                extend_ray(ray)
            ray.forward(1)


def main():
    """
    Main function to run the ray reflection simulation.
    """
    try:
        screen = setup_screen()
        draw_mirrors()

        rays = []
        for angle in ANGLES:
            for ray in RAYS:
                start, color = ray.values()
                ray = create_ray(angle, start, color)
                rays.append(ray)

        for _ in range(ITERATIONS):
            simulate_rays(rays)
            screen.update()

        turtle.done()

    except KeyboardInterrupt:
        print("\nSimulation interrupted by the user. Exiting...")


if __name__ == "__main__":
    main()
