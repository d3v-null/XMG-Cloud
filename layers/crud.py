
from flask import (Blueprint, current_app, redirect, render_template, request,
                   session, url_for)

from layers import oauth2, model

crud = Blueprint('crud', __name__)


@crud.route("/")
def list():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    layers, next_page_token = model.list(cursor=token)

    return render_template(
        "list.html",
        layers=layers,
        next_page_token=next_page_token)


@crud.route('/<id>')
def view(id):
    layer = model.read(id)
    return render_template("view.html", layer=layer)


@crud.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        # If the user is logged in, associate their profile with the new layer.
        if 'profile' in session:
            data['createdBy'] = session['profile']['displayName']
            data['createdById'] = session['profile']['id']

        layer = model.create(data)

        return redirect(url_for('.view', id=layer['id']))

    return render_template("form.html", action="Add", layer={})


@crud.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    layer = model.read(id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        layer = model.update(data, id)

        return redirect(url_for('.view', id=layer['id']))

    return render_template("form.html", action="Edit", layer=layer)


@crud.route('/<id>/delete')
def delete(id):
    model.delete(id)
    return redirect(url_for('.list'))
