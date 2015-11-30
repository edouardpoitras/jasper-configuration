# -*- coding: utf-8-*-
import re
import yaml
from pytz import timezone
from client import plugin
from client import app_utils
from client import jasperpath
from client import pluginstore
from client.mic import Mic

OPTIONS = ["your name", "your location", "your timezone", "my voice"]

class ConfigurationPlugin(plugin.SpeechHandlerPlugin):
    def get_phrases(self):
        return ["CONFIGURATION", "CONFIGURATIONS", "SETTING", "SETTINGS",
                "NAME", "LOCATION", "TIMEZONE", "VOICE"]

    def is_valid(self, text):
        return bool(re.search(r'\b(configuration(s)?|conf|setting(s)?)\b', text, re.IGNORECASE))

    def handle(self, text, mic):
        mic.say('What configuration option would you like to change?')
        for option in OPTIONS:
            mic.say('Would you like to change %s?' %option)
            if app_utils.is_positive(mic.active_listen()):
                func = 'change_%s' %option.replace(' ', '_')
                getattr(self, func)(mic)
                return
        mic.say('No configuration option selected for modification')

    def save_profile(self):
        output_file = open(jasperpath.config('profile.yml'), 'w')
        yaml.dump(self.profile, output_file, default_flow_style=False)

    def clean_input(self, text):
        return text.strip('. ')

    def change_your_name(self, mic):
        mic.say('What is your first name?')
        fname = mic.active_listen()
        fname = self.clean_input(fname).lower().capitalize()
        mic.say('What is your last name?')
        lname = mic.active_listen()
        lname = self.clean_input(lname).lower().capitalize()
        self.profile['first_name'] = fname
        self.profile['last_name'] = lname
        self.save_profile()
        mic.say('Your new name is now %s %s' % (self.profile['first_name'],
                                                self.profile['last_name']))

    def change_your_location(self, mic):
        mic.say('What is your new location?')
        location = mic.active_listen()
        location = self.clean_input(location).capitalize()
        self.profile['location'] = location
        self.save_profile()
        mic.say('Your new location is now %s' % (self.profile['location']))

    def change_your_timezone(self, mic):
        mic.say('What is your new timezone?')
        tz = mic.active_listen()
        tz = self.clean_input(tz).capitalize()
        try:
            timezone(tz)
            self.profile['timezone'] = tz
            self.save_profile()
            mic.say('Your new timezone is now %s' % (self.profile['timezone']))
        except:
            print("Not a valid timezone.")

    def change_my_voice(self, mic):
        current_engine = self.profile['tts_engine'].split('-tts')[0]
        mic.say('My current text-to-speech engine is %s.  ' % current_engine)
        mic.say('What will be my new text-to-speech engine?')
        tts_engine = mic.active_listen()
        tts_engine = self.clean_input(tts_engine)
        if not tts_engine.endswith('-tts'):
            tts_engine = '%s-tts' % tts_engine
        plugins = pluginstore.PluginStore([jasperpath.PLUGIN_PATH])
        plugins.detect_plugins()
        try:
            tts_plugin_info = plugins.get_plugin(tts_engine, category='tts')
        except pluginstore.PluginError, e:
            mic.say(e)
            return
        self.profile['tts_engine'] = tts_engine
        self.save_profile()
        # Need to figure out how to reload TTS plugin.
        # tts_plugin = tts_plugin_info.plugin_class(tts_plugin_info,
        #                                           self.profile)
        # mic = Mic(mic._input_device, mic._output_device,
        #           mic.passive_stt_plugin, mic.active_stt_plugin,
        #           tts_plugin)
        # mic.say('My new voice is now configured')
        mic.say('My new voice is now configured.')
        mic.say('Restart me to hear the changes.')
