#!/usr/bin/env python3
"""
n8n Node Scaffolder

Generates boilerplate code for custom n8n nodes in TypeScript.

Usage:
    python node_scaffolder.py MyService --operations get,create,update,delete
    python node_scaffolder.py --help
"""

import argparse
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime


def to_camel_case(name: str) -> str:
    """Convierte a camelCase."""
    parts = name.replace('-', '_').split('_')
    return parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])


def to_pascal_case(name: str) -> str:
    """Convierte a PascalCase."""
    return ''.join(p.capitalize() for p in name.replace('-', '_').split('_'))


def generate_credential(name: str, output_dir: Path) -> str:
    """Genera el archivo de credenciales."""
    pascal_name = to_pascal_case(name)
    camel_name = to_camel_case(name)
    
    content = f'''import {{
\tIAuthenticateGeneric,
\tICredentialTestRequest,
\tICredentialType,
\tINodeProperties,
}} from 'n8n-workflow';

export class {pascal_name}Api implements ICredentialType {{
\tname = '{camel_name}Api';
\tdisplayName = '{pascal_name} API';
\tdocumentationUrl = 'https://docs.example.com/{camel_name}';

\tproperties: INodeProperties[] = [
\t\t{{
\t\t\tdisplayName: 'API Key',
\t\t\tname: 'apiKey',
\t\t\ttype: 'string',
\t\t\ttypeOptions: {{
\t\t\t\tpassword: true,
\t\t\t}},
\t\t\tdefault: '',
\t\t\trequired: true,
\t\t\tdescription: 'The API key for {pascal_name}',
\t\t}},
\t\t{{
\t\t\tdisplayName: 'Base URL',
\t\t\tname: 'baseUrl',
\t\t\ttype: 'string',
\t\t\tdefault: 'https://api.example.com',
\t\t\tdescription: 'The base URL for the API',
\t\t}},
\t];

\tauthenticate: IAuthenticateGeneric = {{
\t\ttype: 'generic',
\t\tproperties: {{
\t\t\theaders: {{
\t\t\t\tAuthorization: '=Bearer {{{{$credentials.apiKey}}}}',
\t\t\t}},
\t\t}},
\t}};

\ttest: ICredentialTestRequest = {{
\t\trequest: {{
\t\t\tbaseURL: '={{{{$credentials.baseUrl}}}}',
\t\t\turl: '/v1/auth/verify',
\t\t\tmethod: 'GET',
\t\t}},
\t}};
}}
'''
    
    filepath = output_dir / 'credentials' / f'{pascal_name}Api.credentials.ts'
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding='utf-8')
    
    return str(filepath)


def generate_node(
    name: str, 
    operations: List[str], 
    output_dir: Path
) -> str:
    """Genera el archivo principal del nodo."""
    pascal_name = to_pascal_case(name)
    camel_name = to_camel_case(name)
    
    # Generar opciones de operaciones
    operations_options = []
    for op in operations:
        op_lower = op.lower()
        if op_lower == 'get':
            action = f'Get a {camel_name.lower()}'
        elif op_lower == 'create':
            action = f'Create a {camel_name.lower()}'
        elif op_lower == 'update':
            action = f'Update a {camel_name.lower()}'
        elif op_lower == 'delete':
            action = f'Delete a {camel_name.lower()}'
        elif op_lower == 'list':
            action = f'List {camel_name.lower()}s'
        else:
            action = f'{op.capitalize()} a {camel_name.lower()}'
        
        operations_options.append(
            f"\t\t\t{{ name: '{op.capitalize()}', value: '{op_lower}', action: '{action}' }},"
        )
    
    operations_str = '\n'.join(operations_options)
    
    # Generar switch cases para execute
    execute_cases = []
    for op in operations:
        op_lower = op.lower()
        if op_lower == 'get':
            execute_cases.append(f'''
\t\t\t\t\tif (operation === 'get') {{
\t\t\t\t\t\tconst id = this.getNodeParameter('id', i) as string;
\t\t\t\t\t\t
\t\t\t\t\t\tresponseData = await this.helpers.httpRequestWithAuthentication.call(
\t\t\t\t\t\t\tthis,
\t\t\t\t\t\t\t'{camel_name}Api',
\t\t\t\t\t\t\t{{
\t\t\t\t\t\t\t\tmethod: 'GET',
\t\t\t\t\t\t\t\turl: `${{baseUrl}}/v1/resources/${{id}}`,
\t\t\t\t\t\t\t\tjson: true,
\t\t\t\t\t\t\t}}
\t\t\t\t\t\t);
\t\t\t\t\t}}''')
        elif op_lower == 'create':
            execute_cases.append(f'''
\t\t\t\t\tif (operation === 'create') {{
\t\t\t\t\t\tconst additionalFields = this.getNodeParameter('additionalFields', i) as object;
\t\t\t\t\t\t
\t\t\t\t\t\tresponseData = await this.helpers.httpRequestWithAuthentication.call(
\t\t\t\t\t\t\tthis,
\t\t\t\t\t\t\t'{camel_name}Api',
\t\t\t\t\t\t\t{{
\t\t\t\t\t\t\t\tmethod: 'POST',
\t\t\t\t\t\t\t\turl: `${{baseUrl}}/v1/resources`,
\t\t\t\t\t\t\t\tbody: additionalFields,
\t\t\t\t\t\t\t\tjson: true,
\t\t\t\t\t\t\t}}
\t\t\t\t\t\t);
\t\t\t\t\t}}''')
        elif op_lower == 'list':
            execute_cases.append(f'''
\t\t\t\t\tif (operation === 'list') {{
\t\t\t\t\t\tconst limit = this.getNodeParameter('limit', i, 50) as number;
\t\t\t\t\t\t
\t\t\t\t\t\tresponseData = await this.helpers.httpRequestWithAuthentication.call(
\t\t\t\t\t\t\tthis,
\t\t\t\t\t\t\t'{camel_name}Api',
\t\t\t\t\t\t\t{{
\t\t\t\t\t\t\t\tmethod: 'GET',
\t\t\t\t\t\t\t\turl: `${{baseUrl}}/v1/resources`,
\t\t\t\t\t\t\t\tqs: {{ limit }},
\t\t\t\t\t\t\t\tjson: true,
\t\t\t\t\t\t\t}}
\t\t\t\t\t\t);
\t\t\t\t\t\t
\t\t\t\t\t\t// Si devuelve array, expandir items
\t\t\t\t\t\tif (Array.isArray(responseData)) {{
\t\t\t\t\t\t\tfor (const item of responseData) {{
\t\t\t\t\t\t\t\treturnData.push({{ json: item }});
\t\t\t\t\t\t\t}}
\t\t\t\t\t\t\tcontinue;
\t\t\t\t\t\t}}
\t\t\t\t\t}}''')
        elif op_lower == 'update':
            execute_cases.append(f'''
\t\t\t\t\tif (operation === 'update') {{
\t\t\t\t\t\tconst id = this.getNodeParameter('id', i) as string;
\t\t\t\t\t\tconst updateFields = this.getNodeParameter('updateFields', i) as object;
\t\t\t\t\t\t
\t\t\t\t\t\tresponseData = await this.helpers.httpRequestWithAuthentication.call(
\t\t\t\t\t\t\tthis,
\t\t\t\t\t\t\t'{camel_name}Api',
\t\t\t\t\t\t\t{{
\t\t\t\t\t\t\t\tmethod: 'PATCH',
\t\t\t\t\t\t\t\turl: `${{baseUrl}}/v1/resources/${{id}}`,
\t\t\t\t\t\t\t\tbody: updateFields,
\t\t\t\t\t\t\t\tjson: true,
\t\t\t\t\t\t\t}}
\t\t\t\t\t\t);
\t\t\t\t\t}}''')
        elif op_lower == 'delete':
            execute_cases.append(f'''
\t\t\t\t\tif (operation === 'delete') {{
\t\t\t\t\t\tconst id = this.getNodeParameter('id', i) as string;
\t\t\t\t\t\t
\t\t\t\t\t\tresponseData = await this.helpers.httpRequestWithAuthentication.call(
\t\t\t\t\t\t\tthis,
\t\t\t\t\t\t\t'{camel_name}Api',
\t\t\t\t\t\t\t{{
\t\t\t\t\t\t\t\tmethod: 'DELETE',
\t\t\t\t\t\t\t\turl: `${{baseUrl}}/v1/resources/${{id}}`,
\t\t\t\t\t\t\t\tjson: true,
\t\t\t\t\t\t\t}}
\t\t\t\t\t\t);
\t\t\t\t\t}}''')
    
    execute_str = '\n'.join(execute_cases)
    
    content = f'''import {{
\tIExecuteFunctions,
\tINodeExecutionData,
\tINodeType,
\tINodeTypeDescription,
\tNodeApiError,
\tNodeOperationError,
}} from 'n8n-workflow';

export class {pascal_name} implements INodeType {{
\tdescription: INodeTypeDescription = {{
\t\tdisplayName: '{pascal_name}',
\t\tname: '{camel_name}',
\t\ticon: 'file:{camel_name}.svg',
\t\tgroup: ['transform'],
\t\tversion: 1,
\t\tsubtitle: '={{{{$parameter["operation"]}}}}',
\t\tdescription: 'Interact with {pascal_name} API',
\t\tdefaults: {{
\t\t\tname: '{pascal_name}',
\t\t}},
\t\tinputs: ['main'],
\t\toutputs: ['main'],
\t\tcredentials: [
\t\t\t{{
\t\t\t\tname: '{camel_name}Api',
\t\t\t\trequired: true,
\t\t\t}},
\t\t],
\t\tproperties: [
\t\t\t// Operaciones
\t\t\t{{
\t\t\t\tdisplayName: 'Operation',
\t\t\t\tname: 'operation',
\t\t\t\ttype: 'options',
\t\t\t\tnoDataExpression: true,
\t\t\t\toptions: [
{operations_str}
\t\t\t\t],
\t\t\t\tdefault: '{operations[0].lower()}',
\t\t\t}},
\t\t\t
\t\t\t// ID para get, update, delete
\t\t\t{{
\t\t\t\tdisplayName: 'ID',
\t\t\t\tname: 'id',
\t\t\t\ttype: 'string',
\t\t\t\trequired: true,
\t\t\t\tdisplayOptions: {{
\t\t\t\t\tshow: {{
\t\t\t\t\t\toperation: ['get', 'update', 'delete'],
\t\t\t\t\t}},
\t\t\t\t}},
\t\t\t\tdefault: '',
\t\t\t\tdescription: 'The ID of the resource',
\t\t\t}},
\t\t\t
\t\t\t// Limit para list
\t\t\t{{
\t\t\t\tdisplayName: 'Limit',
\t\t\t\tname: 'limit',
\t\t\t\ttype: 'number',
\t\t\t\tdisplayOptions: {{
\t\t\t\t\tshow: {{
\t\t\t\t\t\toperation: ['list'],
\t\t\t\t\t}},
\t\t\t\t}},
\t\t\t\ttypeOptions: {{
\t\t\t\t\tminValue: 1,
\t\t\t\t\tmaxValue: 100,
\t\t\t\t}},
\t\t\t\tdefault: 50,
\t\t\t\tdescription: 'Max number of results to return',
\t\t\t}},
\t\t\t
\t\t\t// Campos adicionales para create
\t\t\t{{
\t\t\t\tdisplayName: 'Additional Fields',
\t\t\t\tname: 'additionalFields',
\t\t\t\ttype: 'collection',
\t\t\t\tplaceholder: 'Add Field',
\t\t\t\tdisplayOptions: {{
\t\t\t\t\tshow: {{
\t\t\t\t\t\toperation: ['create'],
\t\t\t\t\t}},
\t\t\t\t}},
\t\t\t\tdefault: {{}},
\t\t\t\toptions: [
\t\t\t\t\t{{
\t\t\t\t\t\tdisplayName: 'Name',
\t\t\t\t\t\tname: 'name',
\t\t\t\t\t\ttype: 'string',
\t\t\t\t\t\tdefault: '',
\t\t\t\t\t}},
\t\t\t\t\t{{
\t\t\t\t\t\tdisplayName: 'Description',
\t\t\t\t\t\tname: 'description',
\t\t\t\t\t\ttype: 'string',
\t\t\t\t\t\tdefault: '',
\t\t\t\t\t}},
\t\t\t\t],
\t\t\t}},
\t\t\t
\t\t\t// Campos para update
\t\t\t{{
\t\t\t\tdisplayName: 'Update Fields',
\t\t\t\tname: 'updateFields',
\t\t\t\ttype: 'collection',
\t\t\t\tplaceholder: 'Add Field',
\t\t\t\tdisplayOptions: {{
\t\t\t\t\tshow: {{
\t\t\t\t\t\toperation: ['update'],
\t\t\t\t\t}},
\t\t\t\t}},
\t\t\t\tdefault: {{}},
\t\t\t\toptions: [
\t\t\t\t\t{{
\t\t\t\t\t\tdisplayName: 'Name',
\t\t\t\t\t\tname: 'name',
\t\t\t\t\t\ttype: 'string',
\t\t\t\t\t\tdefault: '',
\t\t\t\t\t}},
\t\t\t\t\t{{
\t\t\t\t\t\tdisplayName: 'Description',
\t\t\t\t\t\tname: 'description',
\t\t\t\t\t\ttype: 'string',
\t\t\t\t\t\tdefault: '',
\t\t\t\t\t}},
\t\t\t\t],
\t\t\t}},
\t\t],
\t}};

\tasync execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {{
\t\tconst items = this.getInputData();
\t\tconst returnData: INodeExecutionData[] = [];
\t\t
\t\tconst operation = this.getNodeParameter('operation', 0) as string;
\t\tconst credentials = await this.getCredentials('{camel_name}Api');
\t\tconst baseUrl = credentials.baseUrl as string;
\t\t
\t\tfor (let i = 0; i < items.length; i++) {{
\t\t\ttry {{
\t\t\t\tlet responseData: any;
{execute_str}
\t\t\t\t
\t\t\t\tif (responseData !== undefined) {{
\t\t\t\t\treturnData.push({{ json: responseData }});
\t\t\t\t}}
\t\t\t\t
\t\t\t}} catch (error) {{
\t\t\t\tif (this.continueOnFail()) {{
\t\t\t\t\treturnData.push({{
\t\t\t\t\t\tjson: {{ error: (error as Error).message }},
\t\t\t\t\t\tpairedItem: {{ item: i }},
\t\t\t\t\t}});
\t\t\t\t\tcontinue;
\t\t\t\t}}
\t\t\t\t
\t\t\t\tthrow new NodeApiError(this.getNode(), error as Error, {{ itemIndex: i }});
\t\t\t}}
\t\t}}
\t\t
\t\treturn [returnData];
\t}}
}}
'''
    
    filepath = output_dir / 'nodes' / pascal_name / f'{pascal_name}.node.ts'
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding='utf-8')
    
    return str(filepath)


def generate_package_json(name: str, output_dir: Path) -> str:
    """Genera package.json."""
    pascal_name = to_pascal_case(name)
    camel_name = to_camel_case(name)
    
    content = f'''{{
  "name": "n8n-nodes-{camel_name.lower()}",
  "version": "1.0.0",
  "description": "n8n nodes for {pascal_name} API",
  "keywords": [
    "n8n",
    "n8n-community-node-package"
  ],
  "main": "dist/nodes/{pascal_name}/{pascal_name}.node.js",
  "n8n": {{
    "n8nNodesApiVersion": 1,
    "credentials": [
      "dist/credentials/{pascal_name}Api.credentials.js"
    ],
    "nodes": [
      "dist/nodes/{pascal_name}/{pascal_name}.node.js"
    ]
  }},
  "scripts": {{
    "build": "tsc",
    "dev": "tsc --watch",
    "lint": "eslint . --ext .ts",
    "prepublishOnly": "npm run build"
  }},
  "author": "",
  "license": "MIT",
  "dependencies": {{}},
  "devDependencies": {{
    "@types/node": "^20.0.0",
    "n8n-core": "^1.0.0",
    "n8n-workflow": "^1.0.0",
    "typescript": "^5.0.0"
  }},
  "peerDependencies": {{
    "n8n-workflow": "*"
  }}
}}
'''
    
    filepath = output_dir / 'package.json'
    filepath.write_text(content, encoding='utf-8')
    return str(filepath)


def generate_tsconfig(output_dir: Path) -> str:
    """Genera tsconfig.json."""
    content = '''{
  "compilerOptions": {
    "target": "ES2020",
    "module": "CommonJS",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "resolveJsonModule": true,
    "moduleResolution": "node"
  },
  "include": [
    "nodes/**/*.ts",
    "credentials/**/*.ts"
  ],
  "exclude": [
    "node_modules",
    "dist"
  ]
}
'''
    
    filepath = output_dir / 'tsconfig.json'
    filepath.write_text(content, encoding='utf-8')
    return str(filepath)


def generate_readme(name: str, operations: List[str], output_dir: Path) -> str:
    """Genera README.md."""
    pascal_name = to_pascal_case(name)
    
    ops_list = '\n'.join([f'- **{op.capitalize()}**: {op.capitalize()} resources' for op in operations])
    
    content = f'''# n8n-nodes-{name.lower()}

Custom n8n node for {pascal_name} API integration.

## Operations

{ops_list}

## Installation

### Local Installation

```bash
# Build the node
npm run build

# Link to n8n
npm link
cd ~/.n8n/custom
npm link n8n-nodes-{name.lower()}

# Restart n8n
n8n start
```

### Docker

```dockerfile
FROM n8nio/n8n
RUN cd /home/node && npm install n8n-nodes-{name.lower()}
```

## Configuration

1. Add new credentials of type "{pascal_name} API"
2. Enter your API key
3. (Optional) Modify base URL if using custom endpoint

## Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Watch mode
npm run dev
```

## License

MIT
'''
    
    filepath = output_dir / 'README.md'
    filepath.write_text(content, encoding='utf-8')
    return str(filepath)


def main():
    parser = argparse.ArgumentParser(
        description='Generate n8n custom node boilerplate',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s MyService                          # Basic node
  %(prog)s MyService --operations get,create,update,delete,list
  %(prog)s MyService -o ./output              # Custom output directory
        """
    )
    
    parser.add_argument(
        'name',
        help='Name of the service/node (e.g., MyService)'
    )
    
    parser.add_argument(
        '--operations', '-ops',
        default='get,create,update,delete,list',
        help='Comma-separated operations (default: get,create,update,delete,list)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=None,
        help='Output directory (default: ./n8n-nodes-<name>)'
    )
    
    args = parser.parse_args()
    
    name = args.name
    operations = [op.strip() for op in args.operations.split(',')]
    output_dir = args.output or Path(f'./n8n-nodes-{name.lower()}')
    
    print(f"🚀 Generating n8n node: {name}")
    print(f"📁 Output directory: {output_dir}")
    print(f"⚙️  Operations: {', '.join(operations)}")
    print()
    
    # Crear directorio
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generar archivos
    files_created = []
    
    files_created.append(generate_credential(name, output_dir))
    print(f"✅ Created credentials file")
    
    files_created.append(generate_node(name, operations, output_dir))
    print(f"✅ Created node file")
    
    files_created.append(generate_package_json(name, output_dir))
    print(f"✅ Created package.json")
    
    files_created.append(generate_tsconfig(output_dir))
    print(f"✅ Created tsconfig.json")
    
    files_created.append(generate_readme(name, operations, output_dir))
    print(f"✅ Created README.md")
    
    print()
    print("📦 Next steps:")
    print(f"   cd {output_dir}")
    print("   npm install")
    print("   npm run build")
    print()
    print("🔗 Then link to n8n:")
    print("   npm link")
    print("   n8n start")


if __name__ == '__main__':
    main()
