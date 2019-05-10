import numpy as np
import matplotlib.pyplot as plt
import os




class Simulation():
    def __init__(self, car_number=15):
        self.car_number = car_number
        self.mean_velocity_for_n_car = {}
        self.change_car_number()
        self.velocity_for_step = {}
        # self.tor = Tor(how_many_cars=car_number)

        # self.tor.pop_last_car()

    def update_one_step(self):
        self.tor.update_one_step()

    def set_car_number(self, car_number):
        self.car_number = car_number
        self.change_car_number()

    def change_car_number(self):
        self.tor = Tor(how_many_cars=self.car_number)
        self.mean_velocity_for_n_car[self.car_number] = 0
        Car.radius -= 1

    def simulate_n_steps(self, n, how_often_take_snapshot=501,
                         first_picture=1450, directory='../data',
                         how_often_get_velocity_list=1, **kwargs):

        for step in range(n):
            self.tor.update_one_step()
            if step >= first_picture:
                self.mean_velocity_for_n_car[self.car_number] += self.tor.mean_velocity()
                if step % how_often_take_snapshot == 0:
                    name = 'step{:03.0f}.png'.format(step)
                    filepath = os.path.join(os.getcwd(), directory, name)
                    self.tor.save_picture(filepath, **kwargs)
                if step % how_often_get_velocity_list == 0:
                    self.velocity_for_step[step] = self.tor.get_velocity_for_car_table()
        self.mean_velocity_for_n_car[self.car_number] /= (step - first_picture)  # +-1


class Tor():

    def __init__(self, how_many_cars=30, desirable_distance_factor=1.0):
        self.distance_between_cars = (2 * np.pi) / how_many_cars

        self.radius = Car.radius
        self.plot_params = {"x_limit": Car.radius * 1.1,
                            'figsize': 8}
        self.desirable_distance = self.distance_between_cars * desirable_distance_factor
        self.max_speed = 2 * 0.1  # TODO zmienic to
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
                       label=str("{:2f}".format(car.angle_velocity * 2 * Car.radius * 3.6)))
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

    def mean_velocity(self):
        n = len(self.car_list)
        velocity_sum = 0
        for car in self.car_list:
            velocity_sum += car.angle_velocity
        return (velocity_sum / n) * 2 * Car.radius * 3.6  # w km na h

    def update_one_step(self):
        for car_index, car in enumerate(self.car_list):
            car.update_aceleration(self.next_car(car_index))
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

    def get_velocity_for_car_table(self):
        velocity_dict = {}
        for car_index, car in enumerate(self.car_list):
            velocity_dict[car_index] = car.angle_velocity
        return velocity_dict


class Car:
    radius = 50.0 * 3

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

    def update_aceleration(self, other):
        assert isinstance(other, Car)
        distance = self.calculate_distance(other)
        desirable_distance = self.get_desirable_distance()

        if desirable_distance < distance:
            if self.angle_velocity > self.max_speed:
                self.aceleration = 0
                return
            self.accelerate(distance, desirable_distance)
        elif 0.5 * desirable_distance > distance:
            self.slow_down_fast()
        else:
            self.slow_down(distance, desirable_distance)

        if self.dont_accelerate(other):
            self.aceleration = max(self.aceleration, 0)

    def dont_accelerate(self, other):
        if self.angle_velocity < other.angle_velocity / 2:
            return True
        return False

    def get_desirable_distance(self):
        return (self.angle_velocity ** 2 / (2 * 0.045) + self.angle_velocity / 2) * 2

    def update_velocity(self):

        self.angle_velocity += self.aceleration
        if self.angle_velocity < 0.0:
            self.angle_velocity = 0.0
            self.aceleration = 0.0

    def accelerate(self, distance, desirable_distance, aceleration_speed=2 * 0.0075):
        if distance > 2 * desirable_distance:
            self.aceleration = aceleration_speed
        else:
            self.aceleration = aceleration_speed * (
                        distance - desirable_distance) / desirable_distance + 0.1 * np.random.normal() * aceleration_speed

    def slow_down(self, distance, desirable_distance, aceleration_speed=2 * 0.0075):
        self.aceleration = aceleration_speed * (
                    distance - desirable_distance) / desirable_distance + 0.1 * np.random.normal() * aceleration_speed

    def slow_down_fast(self, aceleration_speed=0.045):
        self.aceleration = -aceleration_speed


if __name__ == '__main__':
    N_STEPS = 1600
    S = Simulation()
    for car_n in [30]:  # 15,71
        S.set_car_number(car_n)
        Car.radius = 165 - car_n
        S.simulate_n_steps(N_STEPS, plot_road=True)

    #    print(S.mean_velocity)
    #    plt.plot(S.mean_velocity)

    for step in S.velocity_for_step:
    #for n in S.velocity_for_step[step]:
        plt.scatter(S.velocity_for_step[step].keys(), S.velocity_for_step[step].values())
        plt.ylim((0.04, 0.1))
        plt.savefig("../data/step{:03.0f}.png".format(step))
        plt.close()
