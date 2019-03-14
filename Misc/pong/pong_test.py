import pytest, time
import mock, asyncio
from pong import *


class MockView():
    def update(self):
        print("Mock View called to update")

class MockModel():
    def update(self, speed):
        pass

class MockIncomingConnection():
    def __init__(self, array_data_to_send, remote_addr = None):
        self.data = array_data_to_send
        self.addr = remote_addr

    async def send_to(self, function, frequency):
        for new_data in self.data:
            await asyncio.sleep(frequency)
            await function(new_data.encode(), self.addr)


async def force_exit(controller,timeout):
    print("entered force exit: {}".format(time.time()))
    await asyncio.sleep(timeout)
    print("forcing exit: {}".format(time.time()))
    controller.exit()

async def async_no_check():
    print("in async no check: {}".format(time.time()))

class TestSuiteForController:
    def setup_method(self):
        with mock.patch('pong.Controller.get_model',side_effect=mock.MagicMock):
            self.basic_controller = Controller()
            self.no_view_controller = Controller()
            self.no_view_controller.views = []

    def test_controller_add_fake_view(self):
        with mock.patch('pong.Controller.add_view',side_effect=MockView) as mock_add_view:
            self.basic_controller.calibrate_speed()
        assert mock_add_view.call_count == 1

    def test_exit_without_starting(self):
        self.no_view_controller.waiting_net_opponent = False
        loop = asyncio.get_event_loop()
        with mock.patch('pong.Controller.calibrate_speed'), mock.patch('pong.Controller.checkspeed'):
            loop.run_until_complete(asyncio.gather(
                self.no_view_controller.run_game(),
                force_exit(self.no_view_controller,1)
            ))

    def test_exit_after_fake_short_game(self):
        self.no_view_controller.waiting_net_opponent = False
        self.no_view_controller.run_update_frequency = 0.45
        force_exit_timeout = 1
        loop = asyncio.get_event_loop()
        with mock.patch('pong.Controller.calibrate_speed'), mock.patch('pong.Controller.checkspeed'), mock.patch('pong.Controller.check_restart', side_effect=async_no_check) as mock_check:
            loop.run_until_complete(asyncio.gather(
                self.no_view_controller.run_game(),
                force_exit(self.no_view_controller,force_exit_timeout)
            ))
        assert mock_check.call_count == int(force_exit_timeout / self.no_view_controller.run_update_frequency) + 1

    def test_run_fake_networked_game(self):
        self.no_view_controller.ball = mock.MagicMock()
        self.no_view_controller.waiting_net_opponent = True
        self.no_view_controller.run_update_frequency = 0.45
        fake_incoming_message = self.no_view_controller.compose_position_message(NETMSG_GAMERUN_ID,[True])
        fake_connection = MockIncomingConnection([fake_incoming_message]*2)
        fake_connection_frequency = 1
        force_exit_timeout = 2
        loop = asyncio.get_event_loop()
        with mock.patch('pong.Controller.calibrate_speed'), mock.patch('pong.Controller.checkspeed'), mock.patch('pong.Controller.check_restart', side_effect=async_no_check) as mock_check:
            loop.run_until_complete(asyncio.gather(
                self.no_view_controller.run_game(),
                fake_connection.send_to(self.no_view_controller.process_message_from_net_opponent,fake_connection_frequency),
                force_exit(self.no_view_controller,force_exit_timeout)
            ))
        assert mock_check.call_count == max(1,int((force_exit_timeout - fake_connection_frequency) / self.no_view_controller.run_update_frequency))

        
