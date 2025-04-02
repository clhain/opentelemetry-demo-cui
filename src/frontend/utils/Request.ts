// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0
import { propagation } from "@opentelemetry/api";

import { AttributeNames } from "./enums/AttributeNames";

interface IRequestParams {
  url: string;
  body?: object;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  queryParams?: Record<string, any>;
  headers?: Record<string, string>;
}

const request = async <T>({
  url = '',
  method = 'GET',
  body,
  queryParams = {},
  headers = {
    'content-type': 'application/json',
  },
}: IRequestParams): Promise<T> => {
  // Hack to make it easier to get the cui into envoy spans via dedicated header
  const baggage = propagation.getActiveBaggage()
  const cui = baggage?.getEntry(AttributeNames.CUI)
  if(cui){
    headers[AttributeNames.CUI] = cui.value;
  }
  const response = await fetch(`${url}?${new URLSearchParams(queryParams).toString()}`, {
    method,
    body: body ? JSON.stringify(body) : undefined,
    headers,
  });

  const responseText = await response.text();

  if (!!responseText) return JSON.parse(responseText);

  return undefined as unknown as T;
};

export default request;
