#!/usr/bin/env python
# coding=utf-8

class Asset(object):
    def __init__(self, sequence_name, shot_number, asset_name, asset_path, asset_type, asset_version, asset_comment, asset_tags, asset_dependency, last_access, creator):
        self.sequence_name = sequence_name
        self.shot_number = shot_number
        self.asset_name = asset_name
        self.asset_path = asset_path
        self.asset_type = asset_type
        self.asset_version = asset_version
        self.asset_comment = asset_comment
        self.asset_tags = asset_tags
        self.asset_dependency = asset_dependency
        self.last_access = last_access
        self.creator = creator


    def __str__(self):
        return "Sequence name: {0} | Shot number: {1} | Asset name: {2} | Asset path: {3} | Asset type: {4} | Asset version: {5} | Asset comment: {6} | Asset tags: {7} | Asset dependency: {8} | Last access: {9} | Creator: {10}".format(self.sequence_name, self.shot_number, self.asset_name, self.asset_path, self.asset_type, self.asset_version, self.asset_comment, self.asset_tags, self.asset_dependency, self.last_access, self.creator)





