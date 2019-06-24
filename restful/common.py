"""Common methods"""
import json
import ast
import logging
import werkzeug.wrappers
import datetime
import re
from odoo.http import request
from odoo import fields

_logger = logging.getLogger(__name__)


def valid_response(data, status=200):
    """Valid Response
    This will be return when the http request was successfully processed."""
    data = {"count": len(data), "data": data}
    """ 
        For date and datetime is used isoformat() to produce a serialized version of it, according to ISO 8601 format,
        YYYY-MM-DDTHH:MM:SS (which is easily decoded by JavaScript)
    """
    return werkzeug.wrappers.Response(
        status=status,
        content_type="application/json; charset=utf-8",
        response=json.dumps(data, default=lambda x: x.isoformat() if x and isinstance(x, datetime.date) else x )
    )


def invalid_response(typ, message=None, status=401):
    """Invalid Response
    This will be the return value whenever the server runs into an error
    either from the client or the server."""
    # return json.dumps({})
    return werkzeug.wrappers.Response(
        status=status,
        content_type="application/json; charset=utf-8",
        response=json.dumps(
            {
                "type": typ,
                "message": str(message)
                if str(message)
                else "wrong arguments (missing validation)",
            }
        ),
    )


def extract_arguments(payloads, offset=0, limit=0, order=None):
    """."""
    fields, domain, payload = [], [], {}
    payload = dict((k, ast.literal_eval(v)) for k, v in payloads.items())
    for d in payload.get("domain"):
        if type(d) == str:
            if d.upper() == 'AND':
                d = '&'
            elif d.upper() == 'OR':
                d = '|'
        elif type(d) == tuple:
            d = list(d)
            
            l = len(d)
            if l and type(d[l-1]) == str:
                if re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}$", d[l-1]):
                    d[l-1] = datetime.datetime.strptime(d[l-1], "%Y-%m-%dT%H:%M:%S")
                elif re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}$", d[l-1]):
                    d[l-1] = datetime.datetime.strptime(d[l-1], "%Y-%m-%d").date()
            d = tuple(d)

        domain.append(d)
    if payload.get("fields"):
        fields += payload.get("fields")
    if payload.get("offset"):
        offset = int(payload["offset"])
    if payload.get("limit"):
        limit = int(payload.get("limit"))
    if payload.get("order"):
        order = payload.get("order")
    return [domain, fields, offset, limit, order]
