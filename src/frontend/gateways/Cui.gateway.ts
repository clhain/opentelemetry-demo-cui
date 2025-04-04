// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

import { useRouter } from 'next/router';
import { CUINames } from '../utils/enums/Cui';


const { PRODUCT_NAME = 'DEMO_SHOP' } = process.env;
const defaultCui = `${PRODUCT_NAME}/${CUINames.UNKNOWN}`


/**
 * Guess at a CUI based on the broser path and /or API Call being made.
 */
const guessCui = (path: string, apiName: string) => {
  const cuiPrefix = "demo_shop/"
  // Process CUIs that map directly to a specific API Call
  switch (apiName) {
    case "addCartItem": {
      return `${PRODUCT_NAME}.${CUINames.ADD_TO_CART}`
    }
    case "emptyCart": {
      return `${PRODUCT_NAME}.${CUINames.EMPTY_CART}`
    }
    case "placeOrder": {
      return `${PRODUCT_NAME}.${CUINames.CHECKOUT}`
    }
    default: {
      break
    }
  }
  // Process CUIs by exact url path
  switch (path) {
    case "/": {
      return `${PRODUCT_NAME}.${CUINames.BROWSE}` 
    }
    case "/cart": {
      return `${PRODUCT_NAME}.${CUINames.VIEW_CART}` 
    }
    default: {
      break
    }
  }

  // Process CUIs with dynamic url paths
  if(path.startsWith('/cart/checkout/')){
    return `${PRODUCT_NAME}.${CUINames.VIEW_ORDER}` 
  }
  // Process CUIs with dynamic url paths
  if(path.startsWith('/cart/checkout/')){
    return `${PRODUCT_NAME}.${CUINames.VIEW_ORDER}` 
  }
  if(path.startsWith('/product/')){
    return `${PRODUCT_NAME}.${CUINames.VIEW_ITEM}` 
  }
  
  return `${PRODUCT_NAME}.${CUINames.UNKNOWN}` 
}


const CUIGateway = () => ({
  getCUI(apiName: string): string {
    if (typeof window === 'undefined') return defaultCui;
    const path = window.location.pathname
    return guessCui(path, apiName)
  }
});

export default CUIGateway();
