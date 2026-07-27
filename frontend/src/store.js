// store.js
// Creates the Redux store (the actual memory box) and plugs in our form slice.

import { configureStore } from '@reduxjs/toolkit'
import formReducer from './formSlice'

export const store = configureStore({
  reducer: {
    form: formReducer,   // our form data lives under the name "form"
  },
})