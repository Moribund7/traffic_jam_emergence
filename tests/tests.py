from Simulation import *

def test_true():
    assert True

def test_car_angele_smaller_than_two_pi():
    car1 = Car(angle=1)
    car2 = Car(angle=0.0)
    car3 = Car(angle=32)
    assert car1.get_position_angle() < 2*np.pi
    assert car2.get_position_angle() < 2 * np.pi
    assert car3.get_position_angle() < 2 * np.pi

def test_distance_for_cars_on_the_same_side():
    car1 = Car(angle=1)
    car2 = Car(angle=0.0)
    assert car1.calculate_distance(car2) == 1.0

def test_distance_for_cars_on_the_oposite_side():
    car1 = Car(angle=6)
    car2 = Car(angle=0.0)
    assert car1.calculate_distance(car2) < .5

def test_distance_reflexive():
    car1 = Car(angle=6)
    car2 = Car(angle=0.0)
    assert car1.calculate_distance(car2) == car2.calculate_distance(car1)

def test_next_car_index():
    tor1=Tor()
    for i in range(len(tor1.car_list)-1):
        assert tor1.car_list[i+1].get_position_angle() == tor1.next_car(i).get_position_angle()


