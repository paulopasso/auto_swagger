def get_context():
    return [
        # User Routes
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Create User",
                "line": {
                    "beginning": 39,
                    "end": 55
                },
                "general_purpose": "Create a new user with name and email"
            },
            "apiDetails": {
                "users": {
                    "endpoint": {
                        "path": "/api/users",
                        "methods": ["POST"],
                        "resourceType": "User"
                    },
                    "parameters": {
                        "body": {
                            "name": { "type": "string", "required": True },
                            "email": { "type": "string", "required": True, "format": "email" }
                        }
                    },
                    "responses": {
                        "success": {
                            "create": {
                                "statusCode": 201,
                                "description": "User created successfully"
                            }
                        },
                        "error": {
                            "400": {
                                "description": "Invalid input parameters",
                                "conditions": ["Missing required fields"]
                            }
                        }
                    }
                }
            }
        },
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Get All Users",
                "line": {
                    "beginning": 57,
                    "end": 59
                },
                "general_purpose": "Retrieve all users"
            },
            "apiDetails": {
                "users": {
                    "endpoint": {
                        "path": "/api/users",
                        "methods": ["GET"],
                        "resourceType": "User"
                    },
                    "responses": {
                        "success": {
                            "get_all": {
                                "statusCode": 200,
                                "description": "List of all users"
                            }
                        }
                    }
                }
            }
        },
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Get User by ID",
                "line": {
                    "beginning": 61,
                    "end": 68
                },
                "general_purpose": "Retrieve a specific user by their ID"
            },
            "apiDetails": {
                "users": {
                    "endpoint": {
                        "path": "/api/users/{id}",
                        "methods": ["GET"],
                        "resourceType": "User"
                    },
                    "parameters": {
                        "path": {
                            "id": { 
                                "type": "integer",
                                "required": True,
                                "description": "User ID"
                            }
                        }
                    },
                    "responses": {
                        "success": {
                            "get_one": {
                                "statusCode": 200,
                                "description": "Single user details"
                            }
                        },
                        "error": {
                            "404": {
                                "description": "User not found",
                                "conditions": ["ID does not exist"]
                            }
                        }
                    }
                }
            }
        },
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Update User",
                "line": {
                    "beginning": 70,
                    "end": 89
                },
                "general_purpose": "Update a user's information"
            },
            "apiDetails": {
                "users": {
                    "endpoint": {
                        "path": "/api/users/{id}",
                        "methods": ["PUT"],
                        "resourceType": "User"
                    },
                    "parameters": {
                        "path": {
                            "id": { 
                                "type": "integer",
                                "required": True,
                                "description": "User ID"
                            }
                        },
                        "body": {
                            "name": { "type": "string", "required": False },
                            "email": { "type": "string", "required": False, "format": "email" }
                        }
                    },
                    "responses": {
                        "success": {
                            "update": {
                                "statusCode": 200,
                                "description": "User updated successfully"
                            }
                        },
                        "error": {
                            "404": {
                                "description": "User not found",
                                "conditions": ["ID does not exist"]
                            },
                            "400": {
                                "description": "Invalid input parameters",
                                "conditions": ["At least one field must be provided"]
                            }
                        }
                    }
                }
            }
        },
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Delete User",
                "line": {
                    "beginning": 91,
                    "end": 98
                },
                "general_purpose": "Delete a user by their ID"
            },
            "apiDetails": {
                "users": {
                    "endpoint": {
                        "path": "/api/users/{id}",
                        "methods": ["DELETE"],
                        "resourceType": "User"
                    },
                    "parameters": {
                        "path": {
                            "id": { 
                                "type": "integer",
                                "required": True,
                                "description": "User ID"
                            }
                        }
                    },
                    "responses": {
                        "success": {
                            "delete": {
                                "statusCode": 204,
                                "description": "User deleted successfully"
                            }
                        },
                        "error": {
                            "404": {
                                "description": "User not found",
                                "conditions": ["ID does not exist"]
                            }
                        }
                    }
                }
            }
        },
        # Item Routes
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Create Item",
                "line": {
                    "beginning": 101,
                    "end": 118
                },
                "general_purpose": "Create a new item with name, description, price, and optional category"
            },
            "apiDetails": {
                "items": {
                    "endpoint": {
                        "path": "/api/items",
                        "methods": ["POST"],
                        "resourceType": "Item"
                    },
                    "parameters": {
                        "body": {
                            "name": { "type": "string", "required": True },
                            "description": { "type": "string", "required": True },
                            "price": { "type": "number", "required": True },
                            "category": { "type": "string", "required": False, "default": "uncategorized" }
                        }
                    },
                    "responses": {
                        "success": {
                            "create": {
                                "statusCode": 201,
                                "description": "Item created successfully"
                            }
                        },
                        "error": {
                            "400": {
                                "description": "Invalid input parameters",
                                "conditions": ["Missing required fields"]
                            }
                        }
                    }
                }
            }
        },
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Get All Items",
                "line": {
                    "beginning": 120,
                    "end": 129
                },
                "general_purpose": "Retrieve all items with optional category filter"
            },
            "apiDetails": {
                "items": {
                    "endpoint": {
                        "path": "/api/items",
                        "methods": ["GET"],
                        "resourceType": "Item"
                    },
                    "parameters": {
                        "query": {
                            "category": {
                                "type": "string",
                                "required": False,
                                "description": "Filter items by category"
                            }
                        }
                    },
                    "responses": {
                        "success": {
                            "get_all": {
                                "statusCode": 200,
                                "description": "List of all items",
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": { "type": "integer" },
                                            "name": { "type": "string" },
                                            "description": { "type": "string" },
                                            "price": { "type": "number" },
                                            "category": { "type": "string" },
                                            "createdAt": { "type": "string", "format": "date-time" }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Get Item by ID",
                "line": {
                    "beginning": 131,
                    "end": 138
                },
                "general_purpose": "Retrieve a specific item by its ID"
            },
            "apiDetails": {
                "items": {
                    "endpoint": {
                        "path": "/api/items/{id}",
                        "methods": ["GET"],
                        "resourceType": "Item"
                    },
                    "parameters": {
                        "path": {
                            "id": { 
                                "type": "integer",
                                "required": True,
                                "description": "Item ID"
                            }
                        }
                    },
                    "responses": {
                        "success": {
                            "get_one": {
                                "statusCode": 200,
                                "description": "Single item details"
                            }
                        },
                        "error": {
                            "404": {
                                "description": "Item not found",
                                "conditions": ["ID does not exist"]
                            }
                        }
                    }
                }
            }
        },
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Update Item",
                "line": {
                    "beginning": 140,
                    "end": 161
                },
                "general_purpose": "Update an item's information"
            },
            "apiDetails": {
                "items": {
                    "endpoint": {
                        "path": "/api/items/{id}",
                        "methods": ["PUT"],
                        "resourceType": "Item"
                    },
                    "parameters": {
                        "path": {
                            "id": { 
                                "type": "integer",
                                "required": True,
                                "description": "Item ID"
                            }
                        },
                        "body": {
                            "name": { "type": "string", "required": False },
                            "description": { "type": "string", "required": False },
                            "price": { "type": "number", "required": False },
                            "category": { "type": "string", "required": False }
                        }
                    },
                    "responses": {
                        "success": {
                            "update": {
                                "statusCode": 200,
                                "description": "Item updated successfully"
                            }
                        },
                        "error": {
                            "404": {
                                "description": "Item not found",
                                "conditions": ["ID does not exist"]
                            },
                            "400": {
                                "description": "Invalid input parameters",
                                "conditions": ["At least one field must be provided"]
                            }
                        }
                    }
                }
            }
        },
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Delete Item",
                "line": {
                    "beginning": 163,
                    "end": 170
                },
                "general_purpose": "Delete an item by its ID"
            },
            "apiDetails": {
                "items": {
                    "endpoint": {
                        "path": "/api/items/{id}",
                        "methods": ["DELETE"],
                        "resourceType": "Item"
                    },
                    "parameters": {
                        "path": {
                            "id": { 
                                "type": "integer",
                                "required": True,
                                "description": "Item ID"
                            }
                        }
                    },
                    "responses": {
                        "success": {
                            "delete": {
                                "statusCode": 204,
                                "description": "Item deleted successfully"
                            }
                        },
                        "error": {
                            "404": {
                                "description": "Item not found",
                                "conditions": ["ID does not exist"]
                            }
                        }
                    }
                }
            }
        }
    ]