// originates from https://github.com/thomasboyt/data/commits/master

var get = Ember.get, set = Ember.set, getPath = Ember.getPath;

DS.localStorageAdapter = DS.Adapter.create({
  
  createRecord: function(store, type, model) {
    var records = this.storage.get(type);
    var id = records.length + 1; // ember-data primary keys are 1-indexed...
    model.set('id', id);
    var data = model.toJSON({associations: true});
    records[id - 1] = data; // but the localStorage array is 0-indexed
    this.storage.set(type, records);

    var self = this;
    this.updateParentArray(type, data, function (allParentsInType, parentType, parentId, parentKey) {
      var parentRecord = allParentsInType[parentId-1];
      parentRecord[parentKey].push(id);
      self.storage.set(parentType, allParentsInType);
      store.load(parentType, parentId, parentRecord);
    });
    
    store.didCreateRecord(model, data);
  },

  updateRecord: function(store, type, model) {
    console.log('updated');

    var id = get(model, 'id');
    var data = model.toJSON({associations: true});

    var records = this.storage.get(type);
    records[id - 1] = data;

    this.storage.set(type, records);

    var self = this;
    this.updateParentArray(type, data, function (allParentsInType, parentType, parentId, arrayKey) {
      var parentRecord = allParentsInType[parentId-1];
      store.load(parentType, parentId, parentRecord);
    });

    store.didUpdateRecord(model, data);
  },

  deleteRecord: function(store, type, model) {
    console.log('deleterecord');
    var id = get(model, 'id');
    var data = model.toJSON({associations: true});

    var records = this.storage.get(type);
    records[id - 1] = null;
    //records.splice(id - 1, 1); //cannot use atm due to how it looks stuff up - need dummies

    this.storage.set(type,records);
    
    var self = this;
    this.updateParentArray(type, data, function (allParentsInType, parentType, parentId, arrayKey) {
      var parentRecord = allParentsInType[parentId-1];
      parentRecord[arrayKey].forEach(function(value, i) {
        if (value == id) {
          parentRecord[arrayKey].splice(i, 1);
        }
      });
      self.storage.set(parentType, allParentsInType);
      store.load(parentType, parentId, parentRecord);
    });
    
    store.didDeleteRecord(model, data);
  },

  find: function(store, type, id) {
    var records = this.storage.get(type);
    store.load(type, id, records[id - 1]);
  },

  findAll: function(store, type) {
    var recs = this.storage.get(type);
    var returnRecs = [];
    recs.forEach(function(val) {
      if (val !== null) {
        returnRecs.push(val);
      }
    });

    if (returnRecs) {
      store.loadMany(type, returnRecs);
    }
  },


  storage: {
    set: function(key, value) {
      localStorage.setItem(key, JSON.stringify(value));
    },
    get: function(key) {
      var value = localStorage.getItem(key);
      value = JSON.parse(value) || [];
      return value;
    }
  },

  //todo: multiple belongsTo associations?
  updateParentArray: function(type, record, update) {
    for (var prop in record) {
      //first, test to see if there is an associated key
      var propKey = prop.replace("_id", ""); //hasMany associations use a foreign key (prop_id)
      var parentType = type.typeForAssociation(propKey);

      if (parentType && typeof record[prop] == "number") {
        var parentId = record[prop];
        var allParents = this.storage.get(parentType);
        var parentRecord = allParents[parentId - 1];
        for (var parentProp in parentRecord) {
          if (parentType.typeForAssociation(parentProp) == type) {
            update(allParents, parentType, parentId, parentProp);
          }
        }
      }
    }
  }

});