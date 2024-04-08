<script setup>
import complaints from '@/assets/complaints.json';
</script>

<template>
  <b-container class="epa-container">
    <b-row>
      <b-col cols="4" class="form">
        <b-form @submit="onSubmit" @reset="onReset" v-if="show">
          <h3>EPD Complaint Tracker</h3>
          <b-form-group id="input-group-1" label="Complaint:" label-for="input-1" description="">
            <b-form-textarea id="input-1" v-model="form.complaint" type="text" placeholder="Enter complaint..." required></b-form-textarea>
          </b-form-group>

          <b-form-group id="input-group-2" label="Location:" label-for="input-2">
            <b-form-input id="input-2" v-model="form.location" placeholder="Enter location..." required></b-form-input>
          </b-form-group>

          <b-form-group id="input-group-3" label="Source Name:" label-for="input-3">
            <b-form-input id="input-3" v-model="form.source_name" placeholder="Enter source name..." required></b-form-input>
          </b-form-group>

          <b-form-group id="input-group-4" label="Source Location:" label-for="input-4">
            <b-form-input id="input-4" v-model="form.source_location" placeholder="Enter source location..." required></b-form-input>
          </b-form-group>

          <b-button type="submit" variant="primary" style="margin-right:10px">Submit</b-button>
        </b-form>
        <!-- <b-card class="mt-3" header="Form Data Result">
          <pre class="m-0">{{ form }}</pre>
        </b-card> -->
      </b-col>

      <b-col cols="8" class="epa-table-container">
        <!-- sticky-header no-border-collapse -->
        <b-table hover responsive small primary-key="_id" sort-by="_id" sortDesc="true"
          :items="items" :fields="fields" class="epa-table"></b-table>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
export default {
  data() {
    const DATA = this.processComplaints(complaints)

    return {
      items: DATA,
      fields: [
        { key: '_id', sortable: true },
        { key: 'complaint', sortable: false },
        { key: 'severity', sortable: true },
        { key: 'location', sortable: false },
        { key: 'date', sortable: false },
        { key: 'source_name', sortable: false },
        { key: 'source_location', sortable: false },
        { key: 'pollutor', sortable: true },
        { key: 'odor', sortable: true },
        { key: 'aqi', sortable: true },
        { key: 'source', sortable: true },
        { key: 'health', sortable: true }
      ],
      form: {
        complaint: '',
        location: '',
        source_name: '',
        source_location: ''
      },
      show: true
    }
  },
  methods: {
    processComplaints(complaints) {
      const ENTRIES = ['pollutor', 'odor', 'aqi', 'source', 'health'];
      let data = JSON.parse(JSON.stringify(complaints));
      ENTRIES.forEach(e => {
        for (let i = 0; i < data.length; i++) {
          data[i][e] = (data[i]['answers'] && data[i]['answers'][e]) ? data[i]['answers'][e] : 0;
        }
      });
      for (let i = 0; i < data.length; i++) {
        delete data[i]['answers']
        data[i]['severity'] = ENTRIES.reduce((acc, e) => acc + (parseInt(data[i][e]) || 0), 0);
        data[i]['date'] = data[i]['date_received'];
        delete data[i]['date_received']
      }
      return data
    },
    onSubmit(event) {
      event.preventDefault()
      let maxId = this.items.reduce((max, item) => Math.max(max, item['_id']), this.items[0]['_id']);

      let data = JSON.parse(JSON.stringify(this.items));
      let form = JSON.parse(JSON.stringify(this.form));

      form['_id'] = parseInt(maxId) + 1
      form['date'] = this.getCurrentDateTime();

      data.push(form);
      this.items = data
    },
    getCurrentDateTime() {
      const now     = new Date();
      const year    = now.getFullYear();
      const month   = String(now.getMonth() + 1).padStart(2, '0');
      const day     = String(now.getDate()).padStart(2, '0');
      const hours   = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      const seconds = String(now.getSeconds()).padStart(2, '0');
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }
  }
}
</script>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}
</style>
