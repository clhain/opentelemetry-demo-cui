// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

import { useRouter } from 'next/router';
import { CUINames, ProductNames } from '../utils/enums/Cui';


const defaultCui = `${ProductNames.DEMO_SHOP}/${CUINames.UNKNOWN}`


/**
 * Guess at a CUI based on the broser path and /or API Call being made.
 */
const guessCui = (path: string, apiName: string) => {
  const cuiPrefix = "demo_shop/"
  // Process CUIs that map directly to a specific API Call
  switch (apiName) {
    case "addCartItem": {
      return `${ProductNames.DEMO_SHOP}.${CUINames.ADD_TO_CART}`
    }
    case "emptyCart": {
      return `${ProductNames.DEMO_SHOP}.${CUINames.EMPTY_CART}`
    }
    case "placeOrder": {
      return `${ProductNames.DEMO_SHOP}.${CUINames.CHECKOUT}`
    }
    default: {
      break
    }
  }
  // Process CUIs by exact url path
  switch (path) {
    case "/": {
      return `${ProductNames.DEMO_SHOP}.${CUINames.BROWSE}` 
    }
    case "/cart": {
      return `${ProductNames.DEMO_SHOP}.${CUINames.VIEW_CART}` 
    }
    default: {
      break
    }
  }

  // Process CUIs with dynamic url paths
  if(path.startsWith('/cart/checkout/')){
    return `${ProductNames.DEMO_SHOP}.${CUINames.VIEW_ORDER}` 
  }
  // Process CUIs with dynamic url paths
  if(path.startsWith('/cart/checkout/')){
    return `${ProductNames.DEMO_SHOP}.${CUINames.VIEW_ORDER}` 
  }
  if(path.startsWith('/product/')){
    return `${ProductNames.DEMO_SHOP}.${CUINames.VIEW_ITEM}` 
  }
  
  return `${ProductNames.DEMO_SHOP}.${CUINames.UNKNOWN}` 
}


const CUIGateway = () => ({
  getCUI(apiName: string): string {
    if (typeof window === 'undefined') return defaultCui;
    const path = window.location.pathname
    return guessCui(path, apiName)
  }
});

export default CUIGateway();
