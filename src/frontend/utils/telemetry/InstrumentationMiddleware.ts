// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

import { NextApiHandler } from 'next';
import { context, Exception, Span, SpanStatusCode, trace } from '@opentelemetry/api';
import { SemanticAttributes } from '@opentelemetry/semantic-conventions';
import { AttributeNames } from '../enums/AttributeNames'
import { metrics } from '@opentelemetry/api';
import { propagation } from "@opentelemetry/api";

const meter = metrics.getMeter('frontend');
const requestCounter = meter.createCounter('app.frontend.requests');

const InstrumentationMiddleware = (handler: NextApiHandler): NextApiHandler => {
  return async (request, response) => {
    const { method, url = '' } = request;
    const [target] = url.split('?');
    const span = trace.getSpan(context.active()) as Span;
    const baggage = propagation.getActiveBaggage() || propagation.createBaggage();
    const activeCui = baggage.getEntry(AttributeNames.CUI)

    let httpStatus = 200;
    try {
      request.headers[AttributeNames.CUI] = activeCui?.value;
      await runWithSpan(span, async () => handler(request, response));
      httpStatus = response.statusCode;
    } catch (error) {
      span.recordException(error as Exception);
      span.setStatus({ code: SpanStatusCode.ERROR });
      httpStatus = 500;
      throw error;
    } finally {
      requestCounter.add(1, { method, target, status: httpStatus });
      if(activeCui){
        span.setAttribute(AttributeNames.CUI, activeCui.value)
      }
      span.setAttribute(SemanticAttributes.HTTP_STATUS_CODE, httpStatus);
    }
  };
};

async function runWithSpan(parentSpan: Span, fn: () => Promise<unknown>) {
  const ctx = trace.setSpan(context.active(), parentSpan);
  return await context.with(ctx, fn);
}

export default InstrumentationMiddleware;
