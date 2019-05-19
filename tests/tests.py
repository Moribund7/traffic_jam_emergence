from Simulation import *
import pytest


def test_true():
    assert True

def test_car_angele_smaller_than_two_pi():
    car1 = Car_binary_aceleration(angle=1,max_speed=1)
    car2 = Car_binary_aceleration(angle=0.0,max_speed=1)
    car3 = Car_binary_aceleration(angle=32,max_speed=1)
    assert car1.get_position_angle() < 2*np.pi
    assert car2.get_position_angle() < 2 * np.pi
    assert car3.get_position_angle() < 2 * np.pi

def test_distance_for_cars_on_the_same_side():
    car1 = Car_binary_aceleration(angle=1,max_speed=1)
    car2 = Car_binary_aceleration(angle=0.0,max_speed=1)
    assert car1.calculate_distance(car2) == 1.0

def test_distance_for_cars_on_the_oposite_side():
    car1 = Car_binary_aceleration(angle=6,max_speed=1)
    car2 = Car_binary_aceleration(angle=0.0,max_speed=1)
    assert car1.calculate_distance(car2) < .5

def test_distance_reflexive():
    car1 = Car_binary_aceleration(angle=6,max_speed=1)
    car2 = Car_binary_aceleration(angle=0.0,max_speed=1)
    assert car1.calculate_distance(car2) == car2.calculate_distance(car1)

def test_next_car_index():
    tor1=Tor(aceleration_model='binary')
    for i in range(len(tor1.car_list)-1):
        assert tor1.car_list[i+1].get_position_angle() == tor1.next_car(i).get_position_angle()

def test_abstract_class_cant_create_object():
    with pytest.raises(TypeError):
        car1=Car_binary_aceleration()

def test_car_inheritance():
    car1=Car_binary_aceleration(1,1)
    car1.update_velocity()

def test_create_diffrent_models():
    car1=Car_binary_aceleration(1, 1)
    car2=CarLinearAcceleration(1, 1)
    car3=Car_function_in_velocity_aceleration(1,1)
    for car in [car1, car2,car3]:
        car.update_velocity()

def test_track_car_number():
    S=Simulation("linear")
    assert len(S.tor.car_list)==15


