import numpy as np
import matplotlib.pyplot as plt
import os


class Simulation():
    def __init__(self):
        self.tor = Tor()

    def update_one_step(self):
        self.tor.update_one_step()

    def simulate_n_steps(self, n, directory='../data',**kwargs):
        for step in range(n):
            self.tor.update_one_step()
            name = 'step{:03.0f}.png'.format(step)
            filepath = os.path.join(os.getcwd(), directory, name)
            self.tor.save_picture(filepath,**kwargs)


class Tor():
    def __init__(self):
        self.car_list = self.init_cars()
        self.radius = Car.radius
        self.plot_params = {"x_limit": Car.radius * 1.1,
                            'figsize': 8}


    def show_tor(self):
        fig, ax = self.draw_tor()
        fig.show()
        plt.close()

    def draw_tor(self,plot_road=False):
        x_limit = self.plot_params['x_limit']
        figsize = self.plot_params['figsize']
        fig, ax = plt.subplots(1, 1, figsize=(figsize, figsize))
        for car in self.car_list:
            ax.scatter(car.get_position_x(), car.get_position_y())
        ax.set(xlim=[-x_limit, x_limit])
        ax.set(ylim=[-x_limit, x_limit])

        if plot_road:
            self.plot_road(ax)
        return fig, ax

    @staticmethod
    def init_cars(how_many_cars=10):
        car_list = []
        for car_index in range(how_many_cars):
            angle = (car_index / how_many_cars) * 2 * np.pi
            car_list.append(Car(angle=angle))
        return car_list

    def update_one_step(self):
        for car in self.car_list:
            car.update_aceleration()
            car.move()

    def save_picture(self, name,**kwargs):
        fig,ax = self.draw_tor(**kwargs)
        fig.savefig(name)
        plt.close()

    def plot_road(self,ax, interior_radius_coeficient=.9, exterior_radius_coeficient=1.1):
        fi = np.linspace(0, 2 * np.pi, 200)
        for r in [interior_radius_coeficient, exterior_radius_coeficient]:
            r *= self.radius
            x = r * np.sin(fi)
            y = r * np.cos(fi)
            ax.plot(x, y, color='black')

class Car():
    radius = 10.0

    def __init__(self, angle, velocity=0.01, aceleration=None):
        self.position_angle = angle
        self.angle_velocity = velocity
        self.aceleration = aceleration

    def get_position_angle(self):
        return self.position_angle

    def get_position_x(self):
        return self.radius * np.sin(self.position_angle)

    def get_position_y(self):
        return self.radius * np.cos(self.position_angle)

    def move(self):
        self.position_angle += self.angle_velocity

    def update_aceleration(self):
        pass


if __name__ == '__main__':
    S = Simulation()
    S.simulate_n_steps(100, plot_road=True)
