Django FileBrowser
==================

**Media-Management for Django 1.4+**. (based on https://github.com/sehmaschine/django-filebrowser)

The FileBrowser is an extension to the `Django <http://www.djangoproject.com>`_ administration interface in order to:

* browse directories on your server and upload/delete/edit/rename files.
* include images/documents to your models/database using the ``FileBrowseField``.
* select images/documents with TinyMCE.

Requirements
------------

FileBrowser 3.4.3 requires

* Django 1.4 (http://www.djangoproject.com)
* PIL (http://www.pythonware.com/products/pil/)

No Grapelli
-----------

This fork removes the dependency on Grappeli.

Installation
------------

    pip install -e git+git://github.com/smacker/django-filebrowser-no-grappelli-django14.git#egg=django-filebrowser

Documentation
-------------

http://readthedocs.org/docs/django-filebrowser/

Translation
-----------

https://www.transifex.net/projects/p/django-filebrowser/