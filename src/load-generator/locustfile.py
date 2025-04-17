#!/usr/bin/python

# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0


import json
import os
import random
import uuid
import logging

from locust import HttpUser, task, between
from locust_plugins.users.playwright import PlaywrightUser, pw, PageWithRetry, event

from opentelemetry import context, baggage, trace
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.jinja2 import Jinja2Instrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource

from openfeature import api
from openfeature.contrib.provider.ofrep import OFREPProvider
from openfeature.contrib.hook.opentelemetry import TracingHook

from playwright.async_api import Route, Request
from enum import Enum

logger_provider = LoggerProvider(resource=Resource.create(
        {
            "service.name": os.environ.get('OTEL_SERVICE_NAME', 'load-generator'),
        }
    ),)
set_logger_provider(logger_provider)

ATTRIBUTE_CUI = "productCui"
PRODUCT_NAME = os.environ.get('PRODUCT_NAME', 'DEMO_SHOP')
class CUINames(Enum):
    ADD_TO_CART = 'ADD_TO_CART'
    BROWSE = 'BROWSE'
    VIEW_ITEM = 'VIEW_ITEM'
    VIEW_CART = 'VIEW_CART'
    VIEW_ORDER = 'VIEW_ORDER'
    EMPTY_CART = 'EMPTY_CART'
    CHECKOUT = 'CHECKOUT'
    UNKNOWN = 'UNKNOWN'

exporter = OTLPLogExporter(insecure=True)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)

# Attach OTLP handler to locust logger
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

exporter = OTLPMetricExporter(insecure=True)
set_meter_provider(MeterProvider([PeriodicExportingMetricReader(exporter)]))

tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)
tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))

def request_hook(span, request):
    if span and request:
        span.set_attribute(ATTRIBUTE_CUI, request.headers.get(ATTRIBUTE_CUI))

# Instrumenting manually to avoid error with locust gevent monkey
Jinja2Instrumentor().instrument()
RequestsInstrumentor().instrument(request_hook=request_hook)
SystemMetricsInstrumentor().instrument()
URLLib3Instrumentor().instrument()
logging.info("Instrumentation complete")

# Initialize Flagd provider
base_url = f"http://{os.environ.get('FLAGD_HOST', 'localhost')}:{os.environ.get('FLAGD_OFREP_PORT', 8016)}"
api.set_provider(OFREPProvider(base_url=base_url))
api.add_hooks([TracingHook()])

def get_flagd_value(FlagName):
    # Initialize OpenFeature
    client = api.get_client()
    return client.get_integer_value(FlagName, 0)

categories = [
    "binoculars",
    "telescopes",
    "accessories",
    "assembly",
    "travel",
    "books",
    None,
]

products = [
    "0PUK6V6EV0",
    "1YMWWN1N4O",
    "2ZYFJ3GM2N",
    "66VCHSJNUP",
    "6E92ZMYYFZ",
    "9SIQT8TOJO",
    "L9ECAV7KIM",
    "LS4PSXUNUM",
    "OLJCESPC7Z",
    "HQTGWGPNH4",
]

people_file = open('people.json')
people = json.load(people_file)

def format_cui(product, cui):
    return f"{product}.{cui.value}"

def update_cui(product, cui):
    ctx = context.get_current()
    c = baggage.set_baggage(ATTRIBUTE_CUI, format_cui(product, cui), context=ctx)
    context.attach(c)

class WebsiteUser(HttpUser):
    wait_time = between(1, 10)

    @task(1)
    def index(self):
        update_cui(PRODUCT_NAME, CUINames.BROWSE)
        self.client.get("/", headers={ATTRIBUTE_CUI: format_cui(PRODUCT_NAME, CUINames.BROWSE)})

    @task(10)
    def browse_product(self):
        update_cui(PRODUCT_NAME, CUINames.BROWSE)
        self.client.get("/api/products/" + random.choice(products), headers={ATTRIBUTE_CUI: format_cui(PRODUCT_NAME, CUINames.BROWSE)})

    @task(3)
    def get_recommendations(self):
        update_cui(PRODUCT_NAME, CUINames.BROWSE)
        params = {
            "productIds": [random.choice(products)],
        }
        self.client.get("/api/recommendations", params=params, headers={ATTRIBUTE_CUI: format_cui(PRODUCT_NAME, CUINames.BROWSE)})

    @task(3)
    def get_ads(self):
        update_cui(PRODUCT_NAME, CUINames.BROWSE)
        params = {
            "contextKeys": [random.choice(categories)],
        }
        self.client.get("/api/data/", params=params, headers={ATTRIBUTE_CUI: format_cui(PRODUCT_NAME, CUINames.BROWSE)})

    @task(3)
    def view_cart(self):
        update_cui(PRODUCT_NAME, CUINames.VIEW_CART)
        self.client.get("/api/cart", headers={ATTRIBUTE_CUI: format_cui(PRODUCT_NAME, CUINames.VIEW_CART)})

    @task(2)
    def add_to_cart(self, user=""):
        if user == "":
            user = str(uuid.uuid1())
        product = random.choice(products)
        update_cui(PRODUCT_NAME, CUINames.BROWSE)
        self.client.get("/api/products/" + product, headers={ATTRIBUTE_CUI: format_cui(PRODUCT_NAME, CUINames.BROWSE)})
        cart_item = {
            "item": {
                "productId": product,
                "quantity": random.choice([1, 2, 3, 4, 5, 10]),
            },
            "userId": user,
        }
        update_cui(PRODUCT_NAME, CUINames.ADD_TO_CART)
        self.client.post("/api/cart", json=cart_item, headers={ATTRIBUTE_CUI: format_cui(PRODUCT_NAME, CUINames.ADD_TO_CART)})

    @task(1)
    def checkout(self):
        # checkout call with an item added to cart
        user = str(uuid.uuid1())
        self.add_to_cart(user=user)
        checkout_person = random.choice(people)
        checkout_person["userId"] = user
        update_cui(PRODUCT_NAME, CUINames.CHECKOUT)
        self.client.post("/api/checkout", json=checkout_person, headers={ATTRIBUTE_CUI: format_cui(PRODUCT_NAME, CUINames.CHECKOUT)})

    @task(1)
    def checkout_multi(self):
        # checkout call which adds 2-4 different items to cart before checkout
        user = str(uuid.uuid1())
        for i in range(random.choice([2, 3, 4])):
            self.add_to_cart(user=user)
        checkout_person = random.choice(people)
        checkout_person["userId"] = user
        update_cui(PRODUCT_NAME, CUINames.CHECKOUT)
        self.client.post("/api/checkout", json=checkout_person, headers={ATTRIBUTE_CUI: format_cui(PRODUCT_NAME, CUINames.CHECKOUT)})

    @task(5)
    def flood_home(self):
        update_cui(PRODUCT_NAME, CUINames.BROWSE)
        for _ in range(0, get_flagd_value("loadGeneratorFloodHomepage")):
            self.client.get("/", headers={ATTRIBUTE_CUI: format_cui(PRODUCT_NAME, CUINames.BROWSE)})

    def on_start(self):
        ctx = baggage.set_baggage("session.id", str(uuid.uuid4()))
        ctx = baggage.set_baggage("synthetic_request", "true", context=ctx)
        context.attach(ctx)
        self.index()


browser_traffic_enabled = os.environ.get("LOCUST_BROWSER_TRAFFIC_ENABLED", "").lower() in ("true", "yes", "on")

if browser_traffic_enabled:
    class WebsiteBrowserUser(PlaywrightUser):
        headless = True  # to use a headless browser, without a GUI

        @task
        @pw
        async def open_cart_page_and_change_currency(self, page: PageWithRetry):
            try:
                page.on("console", lambda msg: print(msg.text))
                await page.route('**/*', add_baggage_header)
                page.set_extra_http_headers({
                    ATTRIBUTE_CUI: format_cui(PRODUCT_NAME, CUINames.VIEW_CART),
                })
                await page.goto("/cart", wait_until="domcontentloaded")
                await page.select_option('[name="currency_code"]', 'CHF')
                await page.wait_for_timeout(2000)  # giving the browser time to export the traces
            except:
                pass

        @task
        @pw
        async def add_product_to_cart(self, page: PageWithRetry):
            try:
                page.on("console", lambda msg: print(msg.text))
                await page.route('**/*', add_baggage_header)
                await page.goto("/", wait_until="domcontentloaded")
                await page.click('p:has-text("Roof Binoculars")', wait_until="domcontentloaded")
                await page.click('button:has-text("Add To Cart")', wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)  # giving the browser time to export the traces
            except:
                pass


async def add_baggage_header(route: Route, request: Request):
    existing_baggage = request.headers.get('baggage', '')
    b = ','.join(filter(None, (existing_baggage, 'synthetic_request=true')))
    existing_cui = request.headers.get(ATTRIBUTE_CUI, '')
    if existing_cui!='':
        b = ','.join(filter(None, (b, f"{ATTRIBUTE_CUI}={existing_cui}")))
    headers = {
        **request.headers,
        'baggage': b
    }
    await route.continue_(headers=headers)
