from functools import wraps
from bucketlist_api.models import User, BucketList
from flask import g, request, abort, current_app, url_for


def get_bucketlist(f):
    @wraps(f)
    def func_wrapper(*args, **kwargs):
        bucketlist_id = kwargs.get('bucketlist_id')
        bucketlist = BucketList.query.get(bucketlist_id)
        if bucketlist is None:
            abort(404)
        g.bucketlist = bucketlist
        return f(*args, **kwargs)
    return func_wrapper


def own_by_user(f):
    @wraps(f)
    def func_wrapper(*args, **kwargs):
        if g.bucketlist.users.id != g.user.id:
            abort(403, "NotPermitted: You can't access bucketlist belonging to"
                  " other users")
        return f(*args, **kwargs)
    return func_wrapper


def paginate(f):
    @wraps(f)
    def func_wrapper(*args, **kwargs):
        query = f(*args, **kwargs)
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit',
                                     current_app.config['DEFAULT_PER_PAGE'],
                                     type=int),
                    current_app.config['MAX_PER_PAGE'])
        q = request.args.get('q')
        page_bucketlist = query.paginate(page=page, per_page=limit)
        bucketlists = page_bucketlist.items
        if not bucketlists:
            abort(404)
        pagination = {
            'page': page_bucketlist.page,
            'number_of_pages': page_bucketlist.pages,
            'total': page_bucketlist.total,
        }
        if page_bucketlist.has_next:
            pagination['next'] = url_for(endpoint=request.endpoint,
                                         limit=limit,
                                         page=page_bucketlist.next_num,
                                         _method='GET', q=q, _external=True,
                                         **kwargs)
        if page_bucketlist.has_prev:
            pagination['previous'] = url_for(endpoint=request.endpoint,
                                             limit=limit, page=page_bucketlist
                                             .prev_num, q=q, _method='GET',
                                             _external=True, **kwargs)
        return {'bucketlists': bucketlists, 'pagination': pagination}, 200
    return func_wrapper
