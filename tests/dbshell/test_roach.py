from django_cockroachdb.client import DatabaseClient

from django.test import SimpleTestCase


class DbshellTests(SimpleTestCase):
    def settings_to_cmd_args_env(self, settings_dict, parameters=None):
        if parameters is None:
            parameters = []
        return DatabaseClient.settings_to_cmd_args_env(settings_dict, parameters)

    def test_fails_with_keyerror_on_incomplete_config(self):
        with self.assertRaises(KeyError):
            self.settings_to_cmd_args_env({})

    def test_basic(self):
        expected_args = ["cockroach", "sql"]
        args, env = self.settings_to_cmd_args_env(
            {
                "NAME": "somedbname",
                "USER": "someuser",
                "PASSWORD": "somepassword",
                "HOST": "somehost",
                "PORT": 444,
                "OPTIONS": {},
            }
        )
        self.assertEqual(args, expected_args)
        self.assertEqual(
            env['COCKROACH_URL'],
            'postgresql://someuser:somepassword@somehost:444/somedbname?'
            'sslmode=disable'
        )

    def test_extra_args(self):
        expected_args = ["cockroach", "sql", "--extra"]
        args, env = self.settings_to_cmd_args_env(
            {
                "NAME": "somedbname",
                "USER": "someuser",
                "PASSWORD": "somepassword",
                "HOST": "somehost",
                "PORT": 444,
                "OPTIONS": {},
            },
            parameters=['--extra'],
        )
        self.assertEqual(args, expected_args)
        self.assertEqual(
            env['COCKROACH_URL'],
            'postgresql://someuser:somepassword@somehost:444/somedbname?'
            'sslmode=disable'
        )

    def test_no_password_or_port(self):
        expected_args = ["cockroach", "sql"]
        args, env = self.settings_to_cmd_args_env(
            {
                "NAME": "somedbname",
                "USER": "someuser",
                "PASSWORD": "",
                "HOST": "somehost",
                "PORT": "",
                "OPTIONS": {},
            }
        )
        self.assertEqual(args, expected_args)
        self.assertEqual(
            env['COCKROACH_URL'],
            'postgresql://someuser:@somehost:/somedbname?sslmode=disable'
        )

    def test_sslrootcert(self):
        expected_args = ["cockroach", "sql"]
        args, env = self.settings_to_cmd_args_env(
            {
                "NAME": "somedbname",
                "USER": "someuser",
                "PASSWORD": "somepassword",
                "HOST": "somehost",
                "PORT": "444",
                "OPTIONS": {
                    'sslmode': 'verify-full',
                    'sslrootcert': 'path/to/ca.crt',
                },
            }
        )
        self.assertEqual(args, expected_args)
        self.assertEqual(
            env['COCKROACH_URL'],
            'postgresql://someuser:somepassword@somehost:444/somedbname?'
            'sslrootcert=path%2Fto%2Fca.crt&sslmode=verify-full'
        )

    def test_sslcert_and_sslkey(self):
        expected_args = ["cockroach", "sql"]
        args, env = self.settings_to_cmd_args_env(
            {
                "NAME": "somedbname",
                "USER": "someuser",
                "PASSWORD": "somepassword",
                "HOST": "somehost",
                "PORT": "444",
                "OPTIONS": {
                    'sslmode': 'verify-full',
                    'sslcert': '/certs/client.myprojectuser.crt',
                    'sslkey': '/certs/client.myprojectuser.key',
                },
            }
        )
        self.assertEqual(args, expected_args)
        self.assertEqual(
            env['COCKROACH_URL'],
            'postgresql://someuser:somepassword@somehost:444/somedbname?'
            'sslcert=%2Fcerts%2Fclient.myprojectuser.crt&'
            'sslkey=%2Fcerts%2Fclient.myprojectuser.key&sslmode=verify-full'
        )

    def test_sslmode_and_options(self):
        expected_args = ["cockroach", "sql"]
        args, env = self.settings_to_cmd_args_env(
            {
                "NAME": "somedbname",
                "USER": "someuser",
                "PASSWORD": "somepassword",
                "HOST": "somehost",
                "PORT": 444,
                "OPTIONS": {
                    'options': '--cluster={routing-id}',
                    'sslmode': 'verify-full',
                },
            }
        )
        self.assertEqual(args, expected_args)
        self.assertEqual(
            env['COCKROACH_URL'],
            'postgresql://someuser:somepassword@somehost:444/somedbname?'
            'sslmode=verify-full&options=--cluster%3D%7Brouting-id%7D'
        )

    def test_sslmode_disable(self):
        expected_args = ["cockroach", "sql"]
        args, env = self.settings_to_cmd_args_env(
            {
                "NAME": "somedbname",
                "USER": "someuser",
                "PASSWORD": "somepassword",
                "HOST": "somehost",
                "PORT": 444,
                "OPTIONS": {
                    'sslmode': 'disable',
                },
            }
        )
        self.assertEqual(args, expected_args)
        self.assertEqual(
            env['COCKROACH_URL'],
            'postgresql://someuser:somepassword@somehost:444/somedbname?'
            'sslmode=disable'
        )
