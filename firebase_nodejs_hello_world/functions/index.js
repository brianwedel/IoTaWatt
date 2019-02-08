const functions = require('firebase-functions');

const admin = require('firebase-admin');
admin.initializeApp(functions.config().firebase);

var db = admin.firestore();
var moment = require('moment');

exports.addMessage = functions.https.onRequest((req, res) => {
    const original = req.query.text;
    return res.send(original);
});

exports.getEnergyUsage = functions.https.onRequest((req, res) => {
    const start_of_today = moment().startOf('Day').valueOf();
    var measRef = db.collection('house').doc('kTwB5pLnvThWmqcqIvaU').collection('meas');
    var query = measRef.where('start_time_ms', '>', start_of_today).get()
        .then(snapshot => {
            var timestamp_list = [];
            snapshot.forEach(doc => {
                timestamp_list.push(doc.data().start_time_ms);
            });
            return res.send(timestamp_list.length.toString());
        })
        .catch(err => {
            return res.send("ERROR", err);
        });
});

// Monitor updates to meas collections, integrate energy over new meas samples, update daily
// energy usage 
exports.updateAccumEnergy = functions.firestore
  .document('house/{houseId}/meas/{measId}')
  .onWrite((change, context) => {
     var houseRef = db.collection('house').doc(context.params.houseId);

     // Integrate over current measurement
     var energy_usage = integrate(change.after.data().samples)

     // update house/{houseId}/daily_energy/{today} document with updated energy usage
  });

