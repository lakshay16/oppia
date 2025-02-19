# Copyright 2018 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Controllers for the practice sessions page."""

from constants import constants
from core.controllers import acl_decorators
from core.controllers import base
from core.domain import dependency_registry
from core.domain import interaction_registry
from core.domain import obj_services
from core.domain import skill_services
from core.domain import topic_services
import feconf
import jinja2


class PracticeSessionsPage(base.BaseHandler):
    """Renders the practice sessions page."""

    @acl_decorators.can_access_topic_viewer_page
    def get(self, topic_name):
        """Handles GET requests."""

        if not constants.ENABLE_NEW_STRUCTURE_PLAYERS:
            raise self.PageNotFoundException

        # Topic cannot be None as an exception will be thrown from its decorator
        # if so.
        topic = topic_services.get_topic_by_name(topic_name)

        interaction_ids = feconf.ALLOWED_QUESTION_INTERACTION_IDS

        interaction_dependency_ids = (
            interaction_registry.Registry.get_deduplicated_dependency_ids(
                interaction_ids))
        dependencies_html, additional_angular_modules = (
            dependency_registry.Registry.get_deps_html_and_angular_modules(
                interaction_dependency_ids))

        interaction_templates = (
            interaction_registry.Registry.get_interaction_html(
                interaction_ids))

        self.values.update({
            'DEFAULT_OBJECT_VALUES': obj_services.get_default_object_values(),
            'additional_angular_modules': additional_angular_modules,
            'INTERACTION_SPECS': interaction_registry.Registry.get_all_specs(),
            'interaction_templates': jinja2.utils.Markup(
                interaction_templates),
            'dependencies_html': jinja2.utils.Markup(dependencies_html),
            'topic_name': topic.name,
        })
        self.render_template('dist/practice-session-page.mainpage.html')


class PracticeSessionsPageDataHandler(base.BaseHandler):
    """Fetches relevant data for the practice sessions page."""

    GET_HANDLER_ERROR_RETURN_TYPE = feconf.HANDLER_TYPE_JSON

    @acl_decorators.can_access_topic_viewer_page
    def get(self, topic_name):

        if not constants.ENABLE_NEW_STRUCTURE_PLAYERS:
            raise self.PageNotFoundException

        # Topic cannot be None as an exception will be thrown from its decorator
        # if so.
        topic = topic_services.get_topic_by_name(topic_name)
        try:
            skills = skill_services.get_multi_skills(topic.get_all_skill_ids())
        except Exception, e:
            raise self.PageNotFoundException(e)
        skills_with_description = {}
        for skill in skills:
            skills_with_description[skill.id] = skill.description

        topic_name = topic.name

        self.values.update({
            'topic_name': topic.name,
            'skills_with_description': skills_with_description
        })
        self.render_json(self.values)
