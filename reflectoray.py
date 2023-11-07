from PIL import Image
from _tkinter import TclError
from rich.progress import Progress
from tempfile import TemporaryDirectory

import argparse
import cv2
import io
import json
import math
import os
import time
import turtle


def parse_arguments():
    """
    Parse command line arguments.

    Returns:
    argparse.Namespace: The namespace object containing the parsed arguments.
    """
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    parser = argparse.ArgumentParser(description="Ray Reflection Simulation")
    parser.add_argument("initial_conditions", nargs='?',
                        default='initial_conditions.json',
                        help="Path to the initial conditions file \
                                (default: initial_conditions.json)")
    parser.add_argument("-i", "--image", type=str,
                        nargs='?', const=f"{timestamp}.png",
                        help="Save the simulation as a png image")
    parser.add_argument("-v", "--video", type=str,
                        nargs='?', const=f"{timestamp}.mp4",
                        help="Record the simulation as a video")
    return parser.parse_args()


def load_initial_conditions(file_path):
    """
    Load the initial conditions from a JSON file.

    Args:
    file_path (str): The path to the JSON file.

    Returns:
    dict: The dictionary containing the initial conditions.
    """
    with open(file_path) as initial_conditions_file:
        initial_conditions = json.load(initial_conditions_file)
    return initial_conditions


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


def draw_mirrors(mirrors):
    """
    Draw the mirrors on the turtle screen.
    """
    for mirror in mirrors:
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


def simulate_rays(rays, mirrors):
    """
    Simulate the reflection of rays off mirrors.

    Args:
    rays (list): List of turtle objects representing rays.
    """
    margin = 2**0.5
    for ray in rays:
        for mirror in mirrors:
            start, end = mirror
            sx, sy = start
            ex, ey = end

            intersection = distance(ray.position(), start, end)
            in_boundary = (sy < ray.ycor() < ey) or (ex < ray.xcor() < sx)

            if intersection <= margin and in_boundary:
                reflection_angle = reflect_ray(ray.heading(), start, end)
                ray.setheading(reflection_angle)
                extend_ray(ray)
            ray.forward(1)


def save_image(screen, output):
    """
    Save the screen as a png image into images folder.

    Args:
    screen (turtle.Screen): The turtle screen object.
    output (str): The path to the output image file.
    """
    eps = screen.getcanvas().postscript()
    img = Image.open(io.BytesIO(eps.encode('utf-8')))
    img.save(output)


def save_video(folder, output, fps=60, codec='mp4v'):
    """
    Save the images in the input folder as a video.

    Args:
    input_folder (str): The path to the input folder.
    output_file (str): The path to the output video file.
    fps (int): The number of frames per second.
    codec (str): The codec to use for the video.
    """
    images = [img for img in os.listdir(folder) if img.endswith(".eps")]
    # Convert eps images to png
    with Progress() as progress:
        task = progress.add_task(
            "Processing images...", total=len(images))
        for image in images:
            img = Image.open(os.path.join(folder, image))
            img.save(os.path.join(folder, image.replace('.eps', '.png')))
            os.remove(os.path.join(folder, image))
            progress.update(task, advance=1)
    images = [img for img in os.listdir(folder) if img.endswith(".png")]
    frame = cv2.imread(os.path.join(folder, images[0]))
    height, width, layers = frame.shape
    video = cv2.VideoWriter(output, cv2.VideoWriter_fourcc(*codec), fps,
                            (width, height))
    with Progress() as progress:
        task = progress.add_task("Compiling video...",
                                 total=len(images))
        for image in images:
            video.write(cv2.imread(os.path.join(folder, image)))
            progress.update(task, advance=1)
    cv2.destroyAllWindows()
    video.release()


def save_output(screen, image, video, tmp):
    if image:
        save_image(screen, image)
        print("Image saved successfully.")

    if video:
        save_video(tmp.name, video)
        print("Video saved successfully.")
        tmp.cleanup()


def main():
    """
    Main function to run the ray reflection simulation.
    """
    try:

        args = parse_arguments()
        initial_conditions = load_initial_conditions(args.initial_conditions)

        # Extracting constants from the loaded initial conditions
        MIRRORS = initial_conditions['mirrors']
        SOURCES = initial_conditions['sources']
        ANGLES = range(initial_conditions['angles']['start'],
                       initial_conditions['angles']['end'],
                       initial_conditions['angles']['step'])
        ITERATIONS = initial_conditions['iterations']

        screen = setup_screen()
        draw_mirrors(MIRRORS)

        rays = []
        for angle in ANGLES:
            for source in SOURCES:
                start, color = source.values()
                ray = create_ray(angle, start, color)
                rays.append(ray)

        if args.video:
            tmp = TemporaryDirectory()

        with Progress() as progress:
            task = progress.add_task(
                "Simulation in progress...", total=ITERATIONS)
            for i in range(ITERATIONS):
                simulate_rays(rays, MIRRORS)
                screen.update()
                if args.video:
                    screen.getcanvas().postscript(file=f"{tmp.name}/{i}.eps")
                progress.update(task, advance=1)

        save_output(screen, args.image, args.video,
                    tmp if args.video else None)

        turtle.done()
        print("Simulation completed successfully.")

    except KeyboardInterrupt:
        print("\nSimulation interrupted by the user. Exiting...")
    except TclError:
        print("Simulation interrupted by the user. Exiting...")


if __name__ == "__main__":
    main()
