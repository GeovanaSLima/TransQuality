#######################  MAIN  #######################

from datetime import timedelta, datetime
import io
import random
import string
from bson import ObjectId
from fastapi import APIRouter, FastAPI, File, Request, status, Depends, HTTPException, Response, Cookie, responses, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import pymongo
from fastapi.templating import Jinja2Templates
import os
from pymongo.mongo_client import MongoClient
import certifi
from fastapi.responses import RedirectResponse, FileResponse,JSONResponse
from fastapi.exceptions import HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import RedirectResponse, HTMLResponse
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from dotenv import load_dotenv
import logging
import asyncio
from reportlab.lib.pagesizes import letter
import tempfile
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable
from mongomock import MongoClient as MockMongoClient

#######################  MODELS  #######################

from mongoengine import Document, IntField, StringField, ReferenceField, BooleanField, DateTimeField
from typing import Any, List, Optional, Dict


#######################  CONFIG  #######################

from pydantic import BaseSettings


#######################  OAUTH  #######################

import base64
from fastapi_jwt_auth import AuthJWT
from jose import JWTError, jwt


#######################  SCHEMAS  #######################

from pydantic import BaseModel, constr, validator


#######################  UTILS  #######################


from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import (OAuth2, OAuth2PasswordBearer,
                              OAuth2PasswordRequestForm)
from fastapi.security.utils import get_authorization_scheme_param
from passlib.context import CryptContext
from reportlab.pdfgen.canvas import Canvas 
from reportlab.lib.styles import getSampleStyleSheet 