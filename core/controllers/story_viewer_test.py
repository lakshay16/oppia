# Copyright 2019 The Oppia Authors. All Rights Reserved.
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

"""Tests for the story viewer page"""

from constants import constants
from core.domain import rights_manager
from core.domain import story_domain
from core.domain import story_services
from core.domain import summary_services
from core.domain import user_services
from core.tests import test_utils
import feconf


class BaseStoryViewerControllerTests(test_utils.GenericTestBase):

    def _record_completion(self, user_id, STORY_ID, node_id):
        """Records the completion of a node in the context of a story."""
        story_services.record_completed_node_in_story_context(
            user_id, STORY_ID, node_id)

    def setUp(self):
        """Completes the sign up process for the various users."""
        super(BaseStoryViewerControllerTests, self).setUp()
        self.VIEWER_EMAIL = 'viewer@example.com'
        self.VIEWER_USERNAME = 'viewer'
        self.signup(self.ADMIN_EMAIL, self.ADMIN_USERNAME)
        self.admin_id = self.get_user_id_from_email(self.ADMIN_EMAIL)
        self.set_admins([self.ADMIN_USERNAME])
        self.admin = user_services.UserActionsInfo(self.admin_id)
        self.login(self.ADMIN_EMAIL)
        self.TOPIC_ID = 'topic_id'
        self.STORY_ID_1 = 'story_id_1'
        self.NODE_ID_1 = 'node_1'
        self.NODE_ID_2 = 'node_2'
        self.NODE_ID_3 = 'node_3'
        self.EXP_ID = 'exp_id'

        self.save_new_valid_exploration(
            self.EXP_ID, self.admin_id, title='Bridges in England',
            category='Architecture', language_code='en')
        rights_manager.publish_exploration(self.admin, self.EXP_ID)
        self.save_new_topic(
            self.TOPIC_ID, 'user', 'Topic', 'A new topic', [], [], [], [], 0)
        story = story_domain.Story.create_default_story(
            self.STORY_ID_1, 'Title', self.TOPIC_ID)
        story.description = ('Description')
        exp_summary_dict = (
            summary_services.get_displayable_exp_summary_dicts_matching_ids(
                [self.EXP_ID], user=self.admin)[0])
        self.node_1 = {
            'id': self.NODE_ID_1,
            'title': 'Title 1',
            'destination_node_ids': ['node_3'],
            'acquired_skill_ids': [],
            'prerequisite_skill_ids': [],
            'outline': '',
            'outline_is_finalized': False,
            'exploration_id': self.EXP_ID,
            'exp_summary_dict': exp_summary_dict,
            'completed': False
        }
        self.node_2 = {
            'id': self.NODE_ID_2,
            'title': 'Title 2',
            'destination_node_ids': ['node_1'],
            'acquired_skill_ids': [],
            'prerequisite_skill_ids': [],
            'outline': '',
            'outline_is_finalized': False,
            'exploration_id': self.EXP_ID,
            'exp_summary_dict': exp_summary_dict,
            'completed': True
        }
        self.node_3 = {
            'id': self.NODE_ID_3,
            'title': 'Title 3',
            'destination_node_ids': [],
            'acquired_skill_ids': [],
            'prerequisite_skill_ids': [],
            'outline': '',
            'outline_is_finalized': False,
            'exploration_id': None
        }
        story.story_contents.nodes = [
            story_domain.StoryNode.from_dict(self.node_1),
            story_domain.StoryNode.from_dict(self.node_2),
            story_domain.StoryNode.from_dict(self.node_3)
        ]
        self.nodes = story.story_contents.nodes
        story.story_contents.initial_node_id = 'node_2'
        story.story_contents.next_node_id = 'node_4'
        story_services.save_new_story(self.admin_id, story)
        story_services.publish_story(self.STORY_ID_1, self.admin_id)
        self.logout()
        self.signup(self.VIEWER_EMAIL, self.VIEWER_USERNAME)
        self.viewer_id = self.get_user_id_from_email(self.VIEWER_EMAIL)
        self.login(self.VIEWER_EMAIL)
        self._record_completion(self.viewer_id, self.STORY_ID_1, self.NODE_ID_2)


class StoryPageTests(BaseStoryViewerControllerTests):
    def test_any_user_can_access_story_viewer_page(self):
        with self.swap(constants, 'ENABLE_NEW_STRUCTURE_PLAYERS', True):
            self.get_html_response(
                '%s/%s' % (feconf.STORY_VIEWER_URL_PREFIX, self.STORY_ID_1))

    def test_get_fails_when_new_structures_not_enabled(self):
        with self.swap(constants, 'ENABLE_NEW_STRUCTURE_PLAYERS', False):
            self.get_html_response(
                '%s/%s' % (feconf.STORY_VIEWER_URL_PREFIX, self.STORY_ID_1),
                expected_status_int=404)


class StoryPageDataHandlerTests(BaseStoryViewerControllerTests):

    def test_can_not_access_story_viewer_page_with_unpublished_story(self):
        new_story_id = 'new_story_id'
        story = story_domain.Story.create_default_story(
            new_story_id, 'Title', 'topic_id')
        story_services.save_new_story(self.admin_id, story)
        with self.swap(constants, 'ENABLE_NEW_STRUCTURE_PLAYERS', True):
            self.get_json(
                '%s/%s' % (feconf.STORY_DATA_HANDLER, new_story_id),
                expected_status_int=404)

    def test_get(self):
        with self.swap(constants, 'ENABLE_NEW_STRUCTURE_PLAYERS', True):
            json_response = self.get_json(
                '%s/%s' % (feconf.STORY_DATA_HANDLER, 'story_id_1'))
            expected_dict = {
                'story_title': 'Title',
                'story_description': 'Description',
                'story_nodes': [self.node_2, self.node_1]
            }
            self.assertDictContainsSubset(expected_dict, json_response)

    def test_get_fails_when_new_structures_not_enabled(self):
        with self.swap(constants, 'ENABLE_NEW_STRUCTURE_PLAYERS', False):
            self.get_json(
                '%s/%s' % (feconf.STORY_DATA_HANDLER, 'story_id_1'),
                expected_status_int=404)
