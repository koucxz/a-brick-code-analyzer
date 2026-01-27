"""
JavaScript/TypeScript 解析器示例
"""

from a_brick_code_analyzer import ParserFactory


def main():
    # JavaScript 示例
    js_code = '''
import React from 'react';
import { useState } from 'react';

function HelloWorld({ name }) {
    const [count, setCount] = useState(0);

    const handleClick = () => {
        if (count < 10) {
            setCount(count + 1);
        } else {
            console.log("Max count reached");
        }
    };

    return (
        <div>
            <h1>Hello, {name}!</h1>
            <p>Count: {count}</p>
            <button onClick={handleClick}>Increment</button>
        </div>
    );
}

class Calculator {
    constructor() {
        this.result = 0;
    }

    add(a, b) {
        return a + b;
    }

    multiply(a, b) {
        let result = 0;
        for (let i = 0; i < b; i++) {
            result += a;
        }
        return result;
    }
}
'''

    # TypeScript 示例
    ts_code = '''
import { Component, OnInit } from '@angular/core';

interface User {
    id: number;
    name: string;
    email: string;
}

class UserService {
    private users: User[] = [];

    addUser(user: User): void {
        this.users.push(user);
    }

    getUserById(id: number): User | undefined {
        return this.users.find(user => user.id === id);
    }

    async fetchUsers(): Promise<User[]> {
        try {
            const response = await fetch('/api/users');
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch users:', error);
            return [];
        }
    }
}

@Component({
    selector: 'app-user-list',
    template: '<div>{{ title }}</div>'
})
export class UserListComponent implements OnInit {
    title: string = 'User List';

    ngOnInit(): void {
        console.log('Component initialized');
    }
}
'''

    print("=== JavaScript 解析结果 ===")
    js_parser = ParserFactory.get_parser("javascript")
    if js_parser:
        js_result = js_parser.parse(js_code)
        print(f"语言: {js_result.language}")
        print(f"总行数: {js_result.total_lines}")
        print(f"代码行数: {js_result.code_lines}")
        print(f"注释行数: {js_result.comment_lines}")
        print(f"空白行数: {js_result.blank_lines}")
        print(f"导入语句: {len(js_result.imports)}")
        print(f"代码节点: {len(js_result.nodes)}")

        functions = [node for node in js_result.nodes if node.node_type.name == 'FUNCTION']
        methods = [node for node in js_result.nodes if node.node_type.name == 'METHOD']
        classes = [node for node in js_result.nodes if node.node_type.name == 'CLASS']
        variables = [node for node in js_result.nodes if node.node_type.name == 'VARIABLE']

        print(f"  - 函数: {len(functions)}")
        print(f"  - 方法: {len(methods)}")
        print(f"  - 类: {len(classes)}")
        print(f"  - 变量: {len(variables)}")

        if js_result.errors:
            print(f"错误: {js_result.errors}")
    else:
        print("JavaScript 解析器不可用（需要安装 tree-sitter）")

    print("\n=== TypeScript 解析结果 ===")
    ts_parser = ParserFactory.get_parser("typescript")
    if ts_parser:
        ts_result = ts_parser.parse(ts_code)
        print(f"语言: {ts_result.language}")
        print(f"总行数: {ts_result.total_lines}")
        print(f"代码行数: {ts_result.code_lines}")
        print(f"注释行数: {ts_result.comment_lines}")
        print(f"空白行数: {ts_result.blank_lines}")
        print(f"导入语句: {len(ts_result.imports)}")
        print(f"代码节点: {len(ts_result.nodes)}")

        functions = [node for node in ts_result.nodes if node.node_type.name == 'FUNCTION']
        methods = [node for node in ts_result.nodes if node.node_type.name == 'METHOD']
        classes = [node for node in ts_result.nodes if node.node_type.name == 'CLASS']
        variables = [node for node in ts_result.nodes if node.node_type.name == 'VARIABLE']

        print(f"  - 函数: {len(functions)}")
        print(f"  - 方法: {len(methods)}")
        print(f"  - 类: {len(classes)}")
        print(f"  - 变量: {len(variables)}")

        if ts_result.errors:
            print(f"错误: {ts_result.errors}")
    else:
        print("TypeScript 解析器不可用（需要安装 tree-sitter）")


if __name__ == "__main__":
    main()