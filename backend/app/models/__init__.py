from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .transaction import *
from .customer import *
from .action import *
from .fraud_alert import *
from .insights import *
from .eval import *
from .kb import *
