"""
A REST API to manage an inventory list of our scout tana <3
"""
from app import app, db
from flask import render_template, redirect, flash, url_for
from app.forms import AddObjectForm, AddLocationForm, EditObjectForm, EditLocationForm, SearchForm
from app.models import Oggetto, Location


@app.route('/')
@app.route('/index')
def index():
    """Main page, showing a list of locations"""

    # TODO add a search bar
    # TODO get a better error handling
    locations = Location.query.all()
    return render_template('index.html', title="Home", locations=locations)


@app.route('/add_object', methods=['GET', 'POST'])
def add_object():
    """Shows an interface to add a new object"""
    form = AddObjectForm()
    if form.validate_on_submit():
        # location_id returns the primary key associated to the selected location
        location_id = Location.query.filter_by(location_name=form.object_location.data.location_name).first().id
        new_object = Oggetto(object_name=form.object_name.data, location_id=location_id,
                             object_notes=form.object_notes.data)
        db.session.add(new_object)
        db.session.commit()
        flash(
            "{} è stato aggiunto all'inventario".format(form.object_name.data, form.object_location.data))
        return redirect(url_for('index'))
    return render_template('add_object.html', title='Aggiungi oggetto', form=form)


@app.route('/edit_object/<int:object_id>', methods=['GET', 'POST'])
def edit_object(object_id):
    """Shows an editing interface to edit a given object"""
    # TODO QuerySelectField non mette di default la location di origine

    # Il form è lo stesso di quello di aggiunta, ma a questo giro gli diamo in input già le info dell'oggetto scelto
    object = Oggetto.query.filter_by(id=object_id).first()
    # name of the location where the object resides
    location_name = Location.query.filter_by(id=object.location_id).first()
    form = EditObjectForm()
    form.object_name.data = object.object_name
    # form.object_location._set_data = location_name
    if form.validate_on_submit():
        location_id = Location.query.filter_by(location_name=form.object_location.data.location_name).first().id
        new_object = {'object_name': form.object_name.data, 'location_id': location_id,
                      'object_notes': form.object_notes.data}
        Oggetto.query.filter_by(id=object_id).update(new_object)
        db.session.commit()
        flash("L'oggetto è stato modificato con successo!")
        return redirect(url_for('index'))
    return render_template('add_object.html', title="Modifica oggetto", form=form)


@app.route('/add_location', methods=['GET', 'POST'])
def add_location():
    """shows an interface to add a new location"""
    form = AddLocationForm()
    if form.validate_on_submit():
        new_location = Location(location_name=form.location_name.data)
        db.session.add(new_location)
        db.session.commit()
        flash("il luogo {} è stato aggiunto all'inventario".format(new_location.location_name))
        return redirect(url_for('add_location'))
    return render_template('add_location.html', title="Aggiungi luogo", form=form)


@app.route('/edit_location/<int:location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    """shows an editing interface for a given location"""
    location = Location.query.filter_by(id=location_id).first()
    form = EditLocationForm()
    form.location_name.data = location.location_name
    if form.validate_on_submit():
        Location.query.filter_by(id=location_id).update({'location_name': form.location_name.data})
        flash('Nome luogo aggiornato con successo!')
        return redirect(url_for('index'))
    return render_template('add_location.html', title="Modifica luogo", form=form)


@app.route('/location/<int:location_id>')
def location(location_id):
    """shows a list of objects from a given location"""

    # a list of Oggetto objects all in the same location
    location_name = Location.query.filter_by(id=location_id).first().location_name
    objects_list = Oggetto.query.filter_by(location_id=location_id).all()
    return render_template('location.html', objects_list=objects_list, location_id=location_id,
                           location_name=location_name)


@app.route('/object/<int:object_id>')
def object(object_id):
    object = Oggetto.query.filter_by(id=object_id).first()
    location_name = Location.query.filter_by(id=object.location_id).first().location_name
    return render_template('object.html', object=object, location_name=location_name)


@app.route('/delete/object/<int:object_id>', methods=['POST'])
def delete_object(object_id):
    """function that removes from database an object with that id"""
    to_delete = Oggetto.query.filter_by(id=object_id).first()
    db.session.delete(to_delete)
    db.session.commit()
    flash("Oggetto eliminato con successo")
    return redirect(url_for('index'))


@app.route('/delete/location/<int:location_id>', methods=['POST'])
def delete_location(location_id):
    """function that removes a location from a database, but only if empty!"""
    if not Oggetto.query.filter_by(location_id=location_id).all():
        # if the location is empty, we can proceed with the removal
        to_delete = Location.query.filter_by(id=location_id).first()
        db.session.delete(to_delete)
        db.session.commit()
        flash("Luogo eliminato con successo")
        return redirect(url_for('index'))
    else:
        flash("Rimuovi tutti gli oggetti dal luogo prima di eliminarlo!")
        return redirect(url_for('location', location_id=location_id))


@app.route('/search', methods=['GET'])
def search():
    form = SearchForm()
    if not form.validate():
        return redirect(url_for('index'))
    results, total = Oggetto.search(form.q.data)

    render_template('search.html', results=results)
