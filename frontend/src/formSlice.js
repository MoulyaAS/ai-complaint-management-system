// formSlice.js
// The Redux "memory box" for our complaint form.
// One box, one job: hold the current form data.

import { createSlice } from '@reduxjs/toolkit'

// The empty form - same fields as schemas.py on the backend. They must match!
const initialState = {
  complainant_name: null,
  product_name: null,
  product_strength: null,
  batch_number: null,
  manufacturing_date: null,
  expiry_date: null,
  affected_quantity: null,
  complaint_description: null,
  severity: null,
  recommended_action: null,
  risk_details: null,
}

const formSlice = createSlice({
  name: 'form',
  initialState,
  reducers: {
    // The ONLY way to change the box: replace it with what the backend sent.
    setForm: (state, action) => {
      return { ...state, ...action.payload }
    },
  },
})

export const { setForm } = formSlice.actions
export default formSlice.reducer