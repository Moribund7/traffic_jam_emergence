import numpy as np
import matplotlib.pyplot as plt
import os


class Simulation():
    def __init__(self):
        self.tor = Tor()
        # self.tor.pop_last_car()

    def update_one_step(self):
        self.tor.update_one_step()

    def simulate_n_steps(self, n, how_often_take_snapshot=1, directory='../data', **kwargs):
        for step in range(n):
            self.tor.update_one_step()
            if step % how_often_take_snapshot == 0:
                name = 'step{:03.0f}.png'.format(step)
                filepath = os.path.join(os.getcwd(), directory, name)
                self.tor.save_picture(filepath, **kwargs)


class Tor():

    def __init__(self, how_many_cars=10, desirable_distance_factor=1.0):
        self.distance_between_cars = (2 * np.pi) / how_many_cars

        self.radius = Car.radius
        self.plot_params = {"x_limit": Car.radius * 1.1,
                            'figsize': 8}
        self.desirable_distance = self.distance_between_cars * desirable_distance_factor
        self.max_speed = 1.5*0.1 #TODO zmienic to
        self.car_list = self.init_cars(how_many_cars, max_speed=self.max_speed)

    def show_tor(self):
        fig, ax = self.draw_tor()
        fig.show()
        plt.close()

    def draw_tor(self, plot_road=False):
        x_limit = self.plot_params['x_limit']
        figsize = self.plot_params['figsize']
        fig, ax = plt.subplots(1, 1, figsize=(figsize, figsize))
        for car in self.car_list:
            ax.scatter(car.get_position_x(), car.get_position_y(),
                       label=str("{:2f}".format(car.angle_velocity*100*3.6)))
        ax.legend()
        ax.set(xlim=[-x_limit, x_limit])
        ax.set(ylim=[-x_limit, x_limit])

        if plot_road:
            self.plot_road(ax)
        return fig, ax

    def init_cars(self, how_many_cars, max_speed):
        car_list = []
        for car_index in range(how_many_cars):
            angle = car_index * self.distance_between_cars
            car_list.append(Car(angle=angle, max_speed=max_speed))
        return car_list

    def update_one_step(self):
        for car_index, car in enumerate(self.car_list):
            car.update_aceleration(self.next_car(car_index), self.desirable_distance)
            car.update_velocity()
        for car in self.car_list:
            car.move()

    def save_picture(self, name, **kwargs):
        fig, ax = self.draw_tor(**kwargs)
        fig.savefig(name)
        plt.close()

    def plot_road(self, ax, interior_radius_coeficient=.9, exterior_radius_coeficient=1.1):
        fi = np.linspace(0, 2 * np.pi, 200)
        for r in [interior_radius_coeficient, exterior_radius_coeficient]:
            r *= self.radius
            x = r * np.sin(fi)
            y = r * np.cos(fi)
            ax.plot(x, y, color='black')

    def pop_last_car(self):
        self.car_list.pop()

    def next_car(self, car_index):
        return self.car_list[(car_index + 1) % len(self.car_list)]


class Car:
    radius = 50.0

    def __init__(self, angle, max_speed, velocity=0.1, aceleration=0.0):
        self.position_angle = angle
        self.angle_velocity = velocity
        self.aceleration = aceleration
        self.normalize_angle()
        self.max_speed = max_speed

    def get_position_angle(self):
        return self.position_angle

    def get_position_x(self):
        return self.radius * np.sin(self.position_angle)

    def get_position_y(self):
        return self.radius * np.cos(self.position_angle)

    def move(self):
        self.position_angle += self.angle_velocity
        self.normalize_angle()

    def normalize_angle(self):
        self.position_angle = self.position_angle % (2 * np.pi)

    def calculate_distance(self, other):
        d1 = abs(self.get_position_angle() - other.get_position_angle())
        d2 = 2 * np.pi - d1
        return min(d1, d2)

    def update_aceleration(self, other, desirable_distance):
        assert isinstance(other, Car)
        distance = self.calculate_distance(other)

        if desirable_distance < distance:
            if self.angle_velocity > self.max_speed:
                self.aceleration = 0
                return
            self.accelerate()
        elif 0.5 * desirable_distance > distance:
            self.slow_down_fast()
        else:
            self.slow_down()

    def update_velocity(self):

        self.angle_velocity += self.aceleration
        if self.angle_velocity < 0.0:
            self.angle_velocity = 0.0
            self.aceleration = 0.0

    def accelerate(self, aceleration_speed=0.0075):
        self.aceleration = aceleration_speed + 0.01 * np.random.normal() * aceleration_speed

    def slow_down(self, aceleration_speed=0.0075):
        self.aceleration = -(aceleration_speed + 0.01 * np.random.normal() * aceleration_speed)

    def slow_down_fast(self,aceleration_speed=0.045):
        self.aceleration = -aceleration_speed


if __name__ == '__main__':
    S = Simulation()
    S.simulate_n_steps(500, plot_road=True)
