MyApp = Ember.Application.create();

MyApp.president = Ember.Object.create({
  firstName: "Barack",
  lastName: "Obama",
  fullName: function() {
    return this.get('firstName') + ' ' + this.get('lastName');
  // Tell Ember that this computed property depends on firstName
  // and lastName
  }.property('firstName', 'lastName')
});