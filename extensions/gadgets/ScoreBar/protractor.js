// Copyright 2014 The Oppia Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @fileoverview End-to-end testing utilities for the ScoreBar gadget.
 */

var objects = require('../../objects/protractor.js');

var customizeGadget = function(elem, title, maxVal, targetParam) {
  elem.element(by.name('form.gadgetSchemaForm'))
    .all(by.tagName('schema-based-unicode-editor')).then(function(items) {
      objects.UnicodeStringEditor(items[0]).setValue(title);
    });

  objects.ParameterNameEditor(elem).setValue(targetParam);

  objects.IntEditor(
    elem.element(by.tagName('schema-based-int-editor')))
    .setValue(maxVal);
};

var expectGadgetPreviewDetailsToMatch = function(elem, title) {
  expect(elem.element(by.css('.protractor-test-scorebar-title')).getText()).toBe(title);
};

var expectGadgetDetailsToMatch = function(elem, title) {
  expect(elem.element(by.css('.protractor-test-scorebar-title'))
    .getText()).toBe(title);
};

exports.customizeGadget = customizeGadget;
exports.expectGadgetPreviewDetailsToMatch = expectGadgetPreviewDetailsToMatch;
exports.expectGadgetDetailsToMatch = expectGadgetDetailsToMatch;
