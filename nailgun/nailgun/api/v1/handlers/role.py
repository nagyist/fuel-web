# -*- coding: utf-8 -*-

# Copyright 2015 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import six

from nailgun.api.v1.handlers import base
from nailgun.api.v1.handlers.base import handle_errors
from nailgun.api.v1.handlers.base import serialize
from nailgun.api.v1.handlers.base import validate
from nailgun.api.v1.validators.role import RoleValidator
from nailgun import errors
from nailgun import objects
from nailgun.objects.serializers.role import RoleSerializer


class RoleMixIn(object):

    def _get_object_or_404(self, obj_type, obj_id):
        obj_cls = {
            'releases': objects.Release,
            'clusters': objects.Cluster,
        }[obj_type]
        return obj_cls, self.get_object_or_404(obj_cls, obj_id)


class RoleHandler(base.SingleHandler, RoleMixIn):

    validator = RoleValidator

    def _check_role(self, obj_cls, obj, role_name):
        if role_name not in obj_cls.get_own_roles(obj):
            raise self.http(
                404,
                "Role '{}' is not found for the {} {}".format(
                    role_name, obj_cls.__name__.lower(), obj.id))

    @handle_errors
    @validate
    @serialize
    def GET(self, obj_type, obj_id, role_name):
        """Retrieve role

        :http:
            * 200 (OK)
            * 404 (no such object found)
        """
        obj_cls, obj = self._get_object_or_404(obj_type, obj_id)
        self._check_role(obj_cls, obj, role_name)
        return RoleSerializer.serialize_from_obj(obj_cls, obj, role_name)

    @handle_errors
    @validate
    @serialize
    def PUT(self, obj_type, obj_id, role_name):
        """Update role

        :http:
            * 200 (OK)
            * 404 (no such object found)
        """
        obj_cls, obj = self._get_object_or_404(obj_type, obj_id)
        self._check_role(obj_cls, obj, role_name)
        data = self.checked_data(
            self.validator.validate_update, instance_cls=obj_cls, instance=obj)
        obj_cls.update_role(obj, data)
        return RoleSerializer.serialize_from_obj(obj_cls, obj, role_name)

    @handle_errors
    def DELETE(self, obj_type, obj_id, role_name):
        """Remove role

        :http:
            * 204 (object successfully deleted)
            * 400 (cannot delete object)
            * 404 (no such object found)
        """
        obj_cls, obj = self._get_object_or_404(obj_type, obj_id)
        self._check_role(obj_cls, obj, role_name)

        try:
            self.validator.validate_delete(obj_cls, obj, role_name)
        except errors.CannotDelete as exc:
            raise self.http(400, exc.message)

        obj_cls.remove_role(obj, role_name)
        raise self.http(204)


class RoleCollectionHandler(base.CollectionHandler, RoleMixIn):

    validator = RoleValidator

    @handle_errors
    @validate
    def POST(self, obj_type, obj_id):
        """Create role for release or cluster

        :http:
            * 201 (object successfully created)
            * 400 (invalid object data specified)
            * 409 (object with such parameters already exists)
        """
        obj_cls, obj = self._get_object_or_404(obj_type, obj_id)
        try:
            data = self.checked_data(
                self.validator.validate_create,
                instance_cls=obj_cls,
                instance=obj)
        except errors.AlreadyExists as exc:
            raise self.http(409, exc.message)

        role_name = data['name']
        obj_cls.update_role(obj, data)
        raise self.http(
            201, RoleSerializer.serialize_from_obj(obj_cls, obj, role_name))

    @handle_errors
    @validate
    @serialize
    def GET(self, obj_type, obj_id):
        obj_cls, obj = self._get_object_or_404(obj_type, obj_id)
        role_names = six.iterkeys(obj_cls.get_roles(obj))
        return [RoleSerializer.serialize_from_obj(obj_cls, obj, name)
                for name in role_names]
