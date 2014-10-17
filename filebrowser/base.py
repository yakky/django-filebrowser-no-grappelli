# coding: utf-8

# PYTHON IMPORTS
import os, shutil, re, datetime, time
import mimetypes

# DJANGO IMPORTS
from django.utils.translation import ugettext as _

# FILEBROWSER IMPORTS
from filebrowser.settings import *
from filebrowser.functions import get_file_type, url_join, get_version_path, \
    get_original_path, sort_by_attr, version_generator, path_strip, url_strip
from django.utils.encoding import smart_str, smart_unicode
from . import settings as fb_settings

# PIL import
if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image


class FileListing():
    """
    The FileListing represents a group of FileObjects/FileDirObjects.
    
    An example::
        
        import os
        from filebrowser.settings import MEDIA_ROOT, DIRECTORY
        from filebrowser.base import FileListing
        
        filelisting = FileListing(os.path.join(MEDIA_ROOT, DIRECTORY), sorting_by='date', sorting_order='desc')
        print filelisting.files_listing_total()
        print filelisting.results_listing_total()
        for fileobject in filelisting.files_listing_total():
            print fileobject.filetype
    """
    # Four variables to store the length of a listing obtained by various listing methods
    # (updated whenever a particular listing method is called).
    _results_listing_total = None
    _results_walk_total = None
    _results_listing_filtered = None
    _results_walk_total = None

    def __init__(self, path, filter_func=None, sorting_by=None,
                 sorting_order=None, site=None):
        self.path = path
        self.filter_func = filter_func
        self.sorting_by = sorting_by
        self.sorting_order = sorting_order
        if not site:
            from filebrowser.sites import site as default_site

            site = default_site
        self.site = site

    _is_folder_stored = None

    @property
    def is_folder(self):
        if self._is_folder_stored == None:
            self._is_folder_stored = self.site.storage.isdir(self.path)
        return self._is_folder_stored

    def listing(self):
        "List all files for path"
        if self.is_folder:
            dirs, files = self.site.storage.listdir(self.path)
            return (f for f in dirs + files)
        return []

    def _walk(self, path, filelisting):
        """
        Recursively walks the path and collects all files and
        directories.

        Danger: Symbolic links can create cycles and this function
        ends up in a regression.
        """
        dirs, files = self.site.storage.listdir(path)

        if dirs:
            for d in dirs:
                self._walk(os.path.join(path, d), filelisting)
                filelisting.extend(
                    [path_strip(os.path.join(path, d), self.site.directory)])

        if files:
            for f in files:
                filelisting.extend(
                    [path_strip(os.path.join(path, f), self.site.directory)])

    def walk(self):
        "Walk all files for path"
        filelisting = []
        if self.is_folder:
            self._walk(self.path, filelisting)
        return filelisting

    # Cached results of files_listing_total (without any filters and sorting applied)
    _fileobjects_total = None

    def files_listing_total(self):
        "Returns FileObjects for all files in listing"
        if self._fileobjects_total == None:
            self._fileobjects_total = []
            for item in self.listing():
                fileobject = FileObject(os.path.join(self.path, item),
                                        site=self.site)
                self._fileobjects_total.append(fileobject)

        files = self._fileobjects_total

        if self.sorting_by:
            files = sort_by_attr(files, self.sorting_by)
        if self.sorting_order == "desc":
            files.reverse()

        self._results_listing_total = len(files)
        return files

    def files_walk_total(self):
        "Returns FileObjects for all files in walk"
        files = []
        for item in self.walk():
            fileobject = FileObject(os.path.join(self.site.directory, item),
                                    site=self.site)
            files.append(fileobject)
        if self.sorting_by:
            files = sort_by_attr(files, self.sorting_by)
        if self.sorting_order == "desc":
            files.reverse()
        self._results_walk_total = len(files)
        return files

    def files_listing_filtered(self):
        "Returns FileObjects for filtered files in listing"
        if self.filter_func:
            listing = filter(self.filter_func, self.files_listing_total())
        else:
            listing = self.files_listing_total()
        self._results_listing_filtered = len(listing)
        return listing

    def files_walk_filtered(self):
        "Returns FileObjects for filtered files in walk"
        if self.filter_func:
            listing = filter(self.filter_func, self.files_walk_total())
        else:
            listing = self.files_walk_total()
        self._results_walk_filtered = len(listing)
        return listing

    def results_listing_total(self):
        "Counter: all files"
        if self._results_listing_total != None:
            return self._results_listing_total
        return len(self.files_listing_total())

    def results_walk_total(self):
        "Counter: all files"
        if self._results_walk_total != None:
            return self._results_walk_total
        return len(self.files_walk_total())

    def results_listing_filtered(self):
        "Counter: filtered files"
        if self._results_listing_filtered != None:
            return self._results_listing_filtered
        return len(self.files_listing_filtered())

    def results_walk_filtered(self):
        "Counter: filtered files"
        if self._results_walk_filtered != None:
            return self._results_walk_filtered
        return len(self.files_walk_filtered())


class FileObject():
    """
    The FileObject represents a file (or directory) on the server.
    
    An example::
        
        from filebrowser.base import FileObject
        
        fileobject = FileObject(path)
    
    where path is a relative path to a storage location.
    """

    def __init__(self, path, site=None):
        if not site:
            from filebrowser.sites import site as default_site

            site = default_site
        self.site = site
        self.path = path
        if self.path.startswith(settings.MEDIA_URL):
            self.path = smart_unicode(self.path).replace(settings.MEDIA_URL, '')
        else:
            self.path = smart_unicode(self.path)
        self.head = os.path.dirname(path)
        self.filename = os.path.basename(path)
        self.filename_lower = self.filename.lower()
        self.filename_root, self.extension = os.path.splitext(self.filename)
        self.mimetype = mimetypes.guess_type(self.filename)

    def __str__(self):
        return smart_unicode(self.path)

    def __unicode__(self):
        return smart_unicode(self.path)

    @property
    def name(self):
        return self.path

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self or "None")

    def __len__(self):
        return len(self.path)

    # GENERAL ATTRIBUTES
    _filetype_stored = None

    @property
    def filetype(self):
        if self._filetype_stored != None:
            return self._filetype_stored
        if self.is_folder:
            self._filetype_stored = 'Folder'
        else:
            self._filetype_stored = get_file_type(self.filename)
        return self._filetype_stored

    _filesize_stored = None

    @property
    def filesize(self):
        if self._filesize_stored != None:
            return self._filesize_stored
        if self.exists():
            self._filesize_stored = self.site.storage.size(self.path)
            return self._filesize_stored
        return None

    _date_stored = None

    @property
    def date(self):
        if self._date_stored != None:
            return self._date_stored
        if self.exists():
            self._date_stored = time.mktime(
                self.site.storage.modified_time(self.path).timetuple())
            return self._date_stored
        return None

    @property
    def datetime(self):
        if self.date:
            return datetime.datetime.fromtimestamp(self.date)
        return None

    _exists_stored = None

    def exists(self):
        if self._exists_stored == None:
            self._exists_stored = self.site.storage.exists(self.path)
        return self._exists_stored

    # PATH/URL ATTRIBUTES
    @property
    def path_relative_directory(self):
        "path relative to DIRECTORY"
        return path_strip(self.path, self.site.directory)

    @property
    def dir(self):
        return os.path.dirname(self.path_relative_directory)

    @property
    def url(self):
        return self.site.storage.url(self.path)

    @property
    def url_full(self):
        """
        Full URL including MEDIA_URL.
        """
        return self.site.storage.url(self.path)

    # IMAGE ATTRIBUTES
    _dimensions_stored = None

    @property
    def dimensions(self):
        if self.filetype != 'Image':
            return None
        if self._dimensions_stored != None:
            return self._dimensions_stored
        try:
            im = Image.open(self.site.storage.open(self.path))
            self._dimensions_stored = im.size
        except:
            pass
        return self._dimensions_stored

    @property
    def width(self):
        if self.dimensions:
            return self.dimensions[0]
        return None

    @property
    def height(self):
        if self.dimensions:
            return self.dimensions[1]
        return None

    @property
    def aspectratio(self):
        if self.dimensions:
            return float(self.width) / float(self.height)
        return None

    @property
    def orientation(self):
        if self.dimensions:
            if self.dimensions[0] >= self.dimensions[1]:
                return "Landscape"
            else:
                return "Portrait"
        return None

    # FOLDER ATTRIBUTES

    @property
    def directory(self):
        return path_strip(self.path, self.site.directory)

    @property
    def folder(self):
        return os.path.dirname(
            path_strip(os.path.join(self.head, ''), self.site.directory))

    _is_folder_stored = None

    @property
    def is_folder(self):
        if self._is_folder_stored == None:
            self._is_folder_stored = self.site.storage.isdir(self.path)
        return self._is_folder_stored

    @property
    def is_empty(self):
        if self.is_folder:
            dirs, files = self.site.storage.listdir(self.path)
            if not dirs and not files:
                return True
        return False

    # VERSIONS

    @property
    def is_version(self):
        tmp = self.filename_root.split("_")
        if tmp[len(tmp) - 1] in VERSIONS:
            return True
        else:
            return False

    @property
    def original(self):
        if self.is_version:
            return FileObject(get_original_path(self.path, site=self.site),
                              site=self.site)
        return self

    @property
    def versions_basedir(self):
        if VERSIONS_BASEDIR and self.site.storage.exists(VERSIONS_BASEDIR):
            return VERSIONS_BASEDIR
        else:
            return self.head

    def version_name(self, version_suffix):
        return self.filename_root + "_" + version_suffix + self.extension

    def versions(self):
        version_list = []
        if self.filetype == "Image":
            for version in VERSIONS:
                version_list.append(os.path.join(self.versions_basedir,
                                                 self.version_name(version)))
        return version_list

    def admin_versions(self):
        version_list = []
        if self.filetype == "Image":
            for version in ADMIN_VERSIONS:
                version_list.append(os.path.join(self.versions_basedir,
                                                 self.version_name(version)))
                # version_list.append(FileObject(os.path.join(self.versions_basedir, self.version_name(version))))
        return version_list

    def version_generate(self, version_suffix):
        version_path = get_version_path(self.path, version_suffix,
                                        site=self.site)
        if not self.site.storage.isfile(version_path):
            version_path = version_generator(self.path, version_suffix,
                                             site=self.site)
        elif self.site.storage.modified_time(
                self.path) > self.site.storage.modified_time(version_path):
            version_path = version_generator(self.path, version_suffix,
                                             force=True, site=self.site)
        return FileObject(version_path, site=self.site)

    # FUNCTIONS

    def delete(self):
        if self.is_folder:
            self.site.storage.rmtree(self.path)
            # shutil.rmtree(self.path)
        else:
            self.site.storage.delete(self.path)

    def delete_versions(self):
        for version in self.versions():
            try:
                self.site.storage.delete(version)
            except:
                pass

    def delete_admin_versions(self):
        for version in self.admin_versions():
            try:
                self.site.storage.delete(version)
            except:
                pass
