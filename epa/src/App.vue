<script setup>
import complaints from '@/assets/complaints.json';
import OpenAI from 'openai';
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

          <b-form-group id="input-group-5" label="OpenAI API Key (Optional):" label-for="input-5" description="Uses ChatGPT to score the severity of a complaint. Create an API key at platform.openai.com/api-keys">
            <b-form-input id="input-5" v-model="form.key" placeholder="sk-..." type="password"></b-form-input>
          </b-form-group>
          
          <b-button v-if="!loading" type="submit" variant="primary" style="margin-right:10px">Submit</b-button>
          <b-button v-else variant="primary" style="margin-right:10px" disabled>
            <b-spinner small style="margin-right:5px"></b-spinner>
            Loading...
          </b-button>
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
const ENTRIES = ['pollutor', 'odor', 'aqi', 'source', 'health'];

const CATEGORIES = {
  'pollutor': "- Look for mentions of a pollutor. This contains mentions of 'plant', 'factory', 'air quality'",
  'odor': "- Look for mentions of smells or odors of a pollutant. This contains mentions of 'smell', 'odor'",
  'aqi': "- Look for specific mentions of air and inhalation. This contains mentions of 'fumes', 'ventilation'",
  'source': "- Look for descriptions of types or identifications of pollutors. This contains mentions of a SOURCE or SPECIFIC TYPE of a pollutant (such as 'benzene')",
  'health': "- Look for complaints of an individual's physical health. This contains physical problems, such as a patient 'hurt' or 'burning' from pollution"
}

const PROMPT = `
Given a categorization, return whether the COMPLAINT mentions the CATEGORY on a scale of 1-3.

SCALE:
- 1: No mention of the problem, this should be ignored
- 2: Vaguely mentions the problem, but it should be followed up with a message
- 3: This problem is fully described and looked into

CATEGORY:
{category}

COMPLAINT:
{complaint}

Only respond with a number (1 or 2 or 3)

Categorization:`

export default {
  
  
  data() {
    const DATA = this.processComplaints(complaints)

    return {
      openai: null,
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
      show: true,
      loading: false
    }
  },
  methods: {
    processComplaints(complaints) {
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
    async onSubmit(event) {
      event.preventDefault()
      this.loading = true;
      let maxId = this.items.reduce((max, item) => Math.max(max, item['_id']), this.items[0]['_id']);

      let data = JSON.parse(JSON.stringify(this.items));
      let form = JSON.parse(JSON.stringify(this.form));

      if (form['key'] !== null && form['key'] !== undefined && form['key'] !== '') {
        this.setup_openai(form['key'])
        delete form['key']

        let answers = await this.gpt_evaluate_complaint(form['complaint'])
        for (let e in answers) {
          form[e] = answers[e];
        }
        form['severity'] = ENTRIES.reduce((acc, e) => acc + (parseInt(form[e]) || 0), 0);
      }

      form['_id'] = parseInt(maxId) + 1
      form['date'] = this.getCurrentDateTime();
      
      data.push(form);
      this.items = data
      this.loading = false;
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
    },
    setup_openai(key) {
      const openai = new OpenAI({ apiKey: key, dangerouslyAllowBrowser: true });
      this.openai = openai
    },
    async gpt_evaluate_complaint(complaint) {
      let answers = {};
      let categories = Object.keys(CATEGORIES);
      for (let j = 0; j < categories.length; j++) {
        let cat = categories[j];
        let out = await this.gpt_generate(PROMPT.replace("{category}", CATEGORIES[cat]).replace("{complaint}", complaint));
        answers[cat] = parseInt(out) || 0;
      }
      return answers;
    },
    async gpt_generate(prompt) {
      const response = await this.openai.chat.completions.create({
        model: 'gpt-3.5-turbo-0125',
        messages: [{ role: 'user', content: prompt }],
        stream: false,
        top_p: 1,
        temperature: 0,
        max_tokens: 1,
      });
      // for await (const chunk of stream) {
      //   console.log(chunk.choices[0]?.delta?.content || '');
      // }
      return response.choices[0]?.message?.content || ''
    }
  }
}
</script>
