import os

import pytest
from click.testing import CliRunner

from notifiers import get_notifier
from notifiers.exceptions import BadArguments


class TestJoin:
    def test_metadata(self):
        j = get_notifier('join')
        assert j.metadata == {
            'base_url': 'https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush',
            'devices_url': 'https://joinjoaomgcd.appspot.com/_ah/api/registration/v1/listDevices',
            'provider_name': 'join',
            'site_url': 'https://joaoapps.com/join/api/'
        }

    @pytest.mark.parametrize('data, message', [
        ({}, 'apikey'),
        ({'apikey': 'foo'}, 'message'),
    ])
    def test_missing_required(self, data, message):
        p = get_notifier('join')
        data['env_prefix'] = 'test'
        with pytest.raises(BadArguments) as e:
            p.notify(**data)
        assert f"'{message}' is a required property" in e.value.message

    def test_defaults(self):
        p = get_notifier('join')
        assert p.defaults == {'deviceId': 'group.all'}

    @pytest.mark.skip('tests fail due to no device connected')
    @pytest.mark.online
    def test_sanity(self):
        p = get_notifier('join')
        data = {'message': 'foo'}
        rsp = p.notify(**data)
        rsp.raise_on_errors()


class TestJoinCLI:
    """Test join specific CLI"""

    def test_join_devices_negative(self):
        from notifiers_cli.providers.join import devices
        runner = CliRunner()
        result = runner.invoke(devices, ['bad_token'])
        assert result.exit_code == -1
        assert not result.output

    @pytest.mark.skip('tests fail due to no device connected')
    @pytest.mark.online
    def test_join_updates_positive(self):
        from notifiers_cli.providers.join import devices
        token = os.environ.get('NOTIFIERS_JOIN_APIKEY')
        assert token

        runner = CliRunner()
        result = runner.invoke(devices, [token])
        assert result.exit_code == 0
        replies = ['You have no devices associated with this apikey', 'Device name: ']
        assert any(reply in result.output for reply in replies)
