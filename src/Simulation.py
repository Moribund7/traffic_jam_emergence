import numpy as np
import matplotlib.pyplot as plt
import os
from abc import ABC, abstractmethod


class Simulation():
    def __init__(self, aceleration_model=None, car_number=10, plot_params=None):
        self.aceleration_model=aceleration_model
        self.plot_params=plot_params
        self.tor = None
        self.car_number = car_number
        self.mean_velocity_for_n_car = {}
        self.change_car_number()
        self.velocity_for_step = {}

    def update_one_step(self):
        self.tor.update_one_step()

    def set_car_number(self, car_number):
        self.car_number = car_number
        self.change_car_number()

    def change_car_number(self):
        self.tor = Tor(aceleration_model=self.aceleration_model,
                       how_many_cars=self.car_number)
        self.mean_velocity_for_n_car[self.car_number] = 0
        Car.radius -= 1

    def simulate_n_steps(self, n,directory='../data',**kwargs):

        plot_params=self.get_plot_params()
        for step in range(n):
            self.update_one_step()
            if step >= plot_params["first_picture"]:
                self.mean_velocity_for_n_car[self.car_number] += self.tor.mean_velocity()
                if step % plot_params["how_often_take_snapshot"] == 0:
                    name = 'step{:03.0f}.png'.format(step)
                    filepath = os.path.join(os.getcwd(), directory, name)
                    self.tor.save_picture(filepath,step=step, **kwargs)
                if step % plot_params["how_often_get_velocity_list"]== 0:
                    self.velocity_for_step[step] = self.tor.get_velocity_for_car_table()
        self.mean_velocity_for_n_car[self.car_number] /= (step - plot_params["first_picture"])  # +-1

    def get_plot_params(self):
        if self.plot_params is None:
            self.plot_params = {"how_often_take_snapshot":501,"first_picture":1450,"how_often_get_velocity_list":1}

        return self.plot_params

    def get_ride_plot(self, n, plot_params=None, plot_road=True,**kwargs):

        if plot_params is None:
            plot_params = {"how_often_take_snapshot": 2,
                           "first_picture": 1,
                           "how_often_get_velocity_list": 10000}
        self.plot_params=plot_params
        self.simulate_n_steps(n,plot_road=plot_road,**kwargs)

    def get_flow(self, N_STEPS, car_n_min, car_n_max, plot_params=None, is_plot_flow=False,
                 is_plot_velocity_for_step=False, how_many_pictures=100):
        if plot_params is None:
            plot_params = {"how_often_take_snapshot": 1000, "first_picture": N_STEPS-how_many_pictures, "how_often_get_velocity_list": 1}
        self.plot_params = plot_params
        for car_n in range(car_n_min, car_n_max+1):  # 15,71
            self.set_car_number(car_n)
            Car.radius = 165 - car_n
            self.simulate_n_steps(N_STEPS)

        if is_plot_flow:
            self.plot_flow()

        if is_plot_velocity_for_step:
            for step in self.velocity_for_step:
                plt.scatter(self.velocity_for_step[step].keys(), self.velocity_for_step[step].values())
                plt.ylim((40, 100))
                plt.xlabel("Numer samochodu")
                plt.ylabel("Prędkość samochodu")
                plt.savefig("../data/step{:03.0f}velocity.png".format(step))
                plt.close()

    def plot_flow(self):
        for car_n in self.mean_velocity_for_n_car:
            plt.scatter(car_n, self.mean_velocity_for_n_car[car_n] * car_n, c='b')
        plt.xlabel("Liczba samochodów")
        plt.ylabel("Przepływ")
        plt.savefig("../data/flow.png")
        plt.close()


class Tor():

    def __init__(self, how_many_cars=10, desirable_distance_factor=1.0, aceleration_model=None):
        self.step_list = []
        self.velocity_list = []
        self.distance_between_cars = (2 * np.pi) / how_many_cars

        self.radius = Car.radius
        self.plot_params = {"x_limit": Car.radius * 1.1,
                            'figsize': 8}
        self.desirable_distance = self.distance_between_cars * desirable_distance_factor
        self.max_speed = 1.5*0.1 #TODO zmienic to jako 1.5 * predkosc poczatkowa lub jako 2*
        self.car_list = self.init_cars(how_many_cars, max_speed=self.max_speed, aceleration_model=aceleration_model)

        self.chosen_car = 7
    def show_tor(self,step,**kwargs):
        fig, ax = self.draw_tor(step,**kwargs)
        fig.show()
        plt.close()

    def draw_tor(self, step, plot_road=False, plot_velocity_scatter=False, is_mark_fasted_car=False):
        x_limit = self.plot_params['x_limit']
        figsize = self.plot_params['figsize']
        if plot_velocity_scatter:
            fig, (ax1,ax2) = plt.subplots(2, 1, figsize=(figsize*3/4, figsize), gridspec_kw = {'hei ght_ratios':[3, 1]})
        else:
            fig, ax1= plt.subplots(1, 1, figsize=(figsize, figsize))

        if is_mark_fasted_car:
            mean_angle_speed = self.get_mean_angle_speed()
        for car_index,car in enumerate(self.car_list):
            if is_mark_fasted_car:
                c = 'r' if car.angle_velocity > 2 * mean_angle_speed else 'b'
            else:
                c='r' if car_index != self.chosen_car else 'g'
            ax1.scatter(car.get_position_x(), car.get_position_y(),
                       label=str("{:2.2f}".format(car.angle_velocity* 2 * Car.radius *3.6))+
                        r'$\frac{km}{h}$',
                        c=c)
        ax1.legend()
        ax1.set(xlim=[-x_limit, x_limit])
        ax1.set(ylim=[-x_limit, x_limit])
        self.step_list.append(step)
        self.velocity_list.append(self.car_list[self.chosen_car].angle_velocity*2 * Car.radius*3.6)
        if plot_velocity_scatter:
            ax2.scatter(self.step_list, self.velocity_list)

        if plot_road:
            self.plot_road(ax1)
        return fig, ax1

    def init_cars(self, how_many_cars, max_speed, aceleration_model):
        car_list = []
        for car_index in range(how_many_cars):
            angle = car_index * self.distance_between_cars
            if aceleration_model == "binary":
                car_list.append(Car_binary_aceleration(angle=angle, max_speed=max_speed))
            elif aceleration_model == 'linear':
                car_list.append(CarLinearAcceleration(angle=angle, max_speed=max_speed))
            elif aceleration_model == 'function_in_velocity':
                car_list.append(Car_function_in_velocity_aceleration(angle=angle, max_speed=max_speed))
            else:
                raise Exception("Wrong aceleration model")
        return car_list

    def mean_velocity(self):
        n = len(self.car_list)
        velocity_sum = 0
        for car in self.car_list:
            velocity_sum += car.angle_velocity
        return (velocity_sum / n) * 2 * Car.radius * 3.6  # w km na h

    def update_one_step(self):
        for car_index, car in enumerate(self.car_list):
            car.update_aceleration(self.next_car(car_index), self.desirable_distance)
            car.update_velocity()
        for car in self.car_list:
            car.move()

    def save_picture(self, name,step, **kwargs):
        fig, ax = self.draw_tor(step,**kwargs)
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
            velocity_dict[car_index] = car.angle_velocity*2 * Car.radius*3.6
        return velocity_dict

    def get_mean_angle_speed(self):
        mean_speed=0
        for car in self.car_list:
            mean_speed += car.angle_velocity
        return mean_speed/len(self.car_list)


class Car(ABC):
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

    @abstractmethod
    def update_aceleration(self, other, desirable_distance):
        raise NotImplementedError("Please Implement this method")

    def update_velocity(self):
        self.angle_velocity += self.aceleration
        if self.angle_velocity < 0.0:
            self.angle_velocity = 0.0
            self.aceleration = 0.0

class Car_binary_aceleration(Car):

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


    def accelerate(self, aceleration_speed=0.0075):
        self.aceleration = aceleration_speed + 0.01 * np.random.normal() * aceleration_speed

    def slow_down(self, aceleration_speed=0.0075):
        self.aceleration = -(aceleration_speed + 0.01 * np.random.normal() * aceleration_speed)

    def slow_down_fast(self,aceleration_speed=0.045):
        self.aceleration = -aceleration_speed


class CarLinearAcceleration(Car):

    def update_aceleration(self, other, desirable_distance):
        assert isinstance(other, Car)
        distance = self.calculate_distance(other)

        if desirable_distance < distance:
            if self.angle_velocity > self.max_speed:
                self.aceleration = 0
                return
            self.accelerate(distance,desirable_distance)
        elif 0.5 * desirable_distance > distance:
            self.slow_down_fast()
        else:
            self.slow_down(distance,desirable_distance)

    def accelerate(self,distance,desirable_distance, aceleration_speed=2*0.0075):
        if distance > 2 * desirable_distance:
            self.aceleration = aceleration_speed
        else:
            self.aceleration = aceleration_speed * (distance-desirable_distance) / desirable_distance + 0.01 * np.random.normal() * aceleration_speed

    def slow_down(self,distance,desirable_distance, aceleration_speed=4*0.0075):
        self.aceleration = aceleration_speed * (distance-desirable_distance) / desirable_distance + 0.01 * np.random.normal() * aceleration_speed

    def slow_down_fast(self,aceleration_speed=0.045):
        self.aceleration = -aceleration_speed


class Car_function_in_velocity_aceleration(Car):

    def update_aceleration(self, other, redundant_argument):
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

    def plot_ride_some_snaps():
        S = Simulation(aceleration_model='linear')
        plot_params={"how_often_take_snapshot": 2,
                               "first_picture": 100,
                               "how_often_get_velocity_list": 10000}
        S.get_ride_plot(200,plot_params=plot_params)


    def plot_velocity_for_cars():
        S = Simulation(aceleration_model='function_in_velocity')
        S.get_flow(1500, car_n_min=30, car_n_max=30, is_plot_velocity_for_step=True,
                   how_many_pictures=100)

    def plot_ride_fasted_car():
        S = Simulation(aceleration_model='linear')
        plot_params = {"how_often_take_snapshot": 2,
                       "first_picture": 100,
                       "how_often_get_velocity_list": 10000}
        S.get_ride_plot(200, plot_params=plot_params,is_mark_fasted_car=True)

    def plot_flow():
        S = Simulation(aceleration_model="function_in_velocity")
        S.get_flow(1100, car_n_min=10, car_n_max=80, is_plot_flow=True)

    plot_flow()

    def plot_flow_vs_models():
        S_b=Simulation(aceleration_model="binary")
        S_l=Simulation(aceleration_model="linear")
        S_f=Simulation(aceleration_model="function_in_velocity")
        models=[S_b,S_l,S_f]
        color={"binary":'r',"linear":'g',"function_in_velocity":'b'}

        for model in models:
            model.get_flow(1100, car_n_min=10, car_n_max=80)

        for model in models:
            for car_n in model.mean_velocity_for_n_car:
                plt.scatter(car_n, model.mean_velocity_for_n_car[car_n] * car_n,
                            c=color[model.aceleration_model],
                            label=model.aceleration_model)
        plt.xlabel("Liczba samochodów")
        plt.ylabel("Przepływ")
        plt.legend()
        plt.savefig("../data/flow.png")
        plt.close()


