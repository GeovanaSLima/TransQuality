from typing import List, Optional
from fastapi import Request


class UserCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str] = None
        self.name: Optional[str] = None
        self.role: Optional[str] = None
        self.password: Optional[str] = None
        self.passwordConfirm: Optional[str] = None
    
    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.name = form.get("name")
        self.role = form.get("role")
        self.password = form.get("password")
        self.passwordConfirm = form.get("passwordConfirm")

    async def is_valid(self):
        if not self.username or not len(self.username) > 3:
            self.errors.append("Username should be > 3 chars")
        if not self.name:
            self.errors.append("Name is required")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("Password must be > 4 chars")
        if not self.passwordConfirm or not len(self.password) >= 4:
            self.errors.append("Confirm Password must be > 4 chars")
        if not self.password == self.passwordConfirm:
            self.errors.append("Passwords are not the same")
        if not self.errors:
            return True
        return False
    
    
class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")
    
    async def is_valid(self):
        if not self.username:
            self.errors.append("Username is Required")
        if not self.password or len(self.password) < 4:
            self.errors.append("A valid password is required")
        if not self.errors:
            return True
        return False
    