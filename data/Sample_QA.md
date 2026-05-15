# 📘 AI Research Assistant – Knowledge Q&A  

This file contains important questions and answers from different subjects, based on the textbooks integrated into the assistant.  

---

## 📘 Algorithms & Data Structures (CLRS, Discrete Math)  

**Q: What is the difference between merge sort and quick sort?**  
- Merge Sort: Divide-and-conquer, stable, O(n log n) in all cases, requires extra space.  
- Quick Sort: Divide-and-conquer, unstable, average O(n log n), worst O(n²), in-place.  

**Q: Explain dynamic programming with an example.**  
- Dynamic Programming (DP) is solving problems by breaking them into subproblems and storing solutions to avoid recomputation.  
- Example: Fibonacci sequence using memoization instead of recalculating each term.  

**Q: What is Dijkstra’s algorithm used for?**  
- It finds the shortest path from a source node to all other nodes in a weighted graph (with non-negative weights).  

**Q: State and explain the Master Theorem.**  
- Provides asymptotic analysis for divide-and-conquer recurrences of the form:  
  `T(n) = aT(n/b) + f(n)`  
  Cases determine if the solution is O(n^log_b(a)), O(n^log_b(a) * log n), or O(f(n)).  

**Q: What is the difference between P, NP, and NP-complete problems?**  
- P: Problems solvable in polynomial time.  
- NP: Problems verifiable in polynomial time.  
- NP-Complete: Hardest problems in NP; if one is solved in P, all NP problems can be solved in P.  

---

## 💻 Operating Systems  

**Q: Explain the difference between a process and a thread.**  
- Process: Independent program with its own memory space.  
- Thread: Lightweight unit of execution within a process, shares memory.  

**Q: What is deadlock? Describe its conditions.**  
- Deadlock: A state where processes wait indefinitely for resources.  
- Conditions (Coffman’s): Mutual exclusion, hold & wait, no preemption, circular wait.  

**Q: Explain paging vs segmentation.**  
- Paging: Divides memory into fixed-size blocks.  
- Segmentation: Divides memory into variable-size logical segments.  

**Q: What are scheduling algorithms in operating systems?**  
- Methods to decide process execution order, e.g., FCFS, SJF, Round Robin, Priority Scheduling.  

**Q: What are the differences between user mode and kernel mode?**  
- User Mode: Limited access, cannot execute privileged instructions.  
- Kernel Mode: Full system access, executes OS instructions.  

---

## 🌐 Computer Networking  

**Q: What are the 7 layers of the OSI model?**  
1. Physical  
2. Data Link  
3. Network  
4. Transport  
5. Session  
6. Presentation  
7. Application  

**Q: Explain the difference between TCP and UDP.**  
- TCP: Reliable, connection-oriented, error checking, ordered delivery.  
- UDP: Unreliable, connectionless, faster, used for streaming/gaming.  

**Q: What is IP addressing and how does it work?**  
- Unique identifier for devices on a network.  
- IPv4 (32-bit) and IPv6 (128-bit). Used for routing data packets.  

**Q: Explain DNS and its role in networking.**  
- Domain Name System translates domain names into IP addresses for communication.  

**Q: What is the difference between hub, switch, and router?**  
- Hub: Broadcasts data to all ports.  
- Switch: Sends data to specific device (MAC-based).  
- Router: Connects multiple networks, routes based on IP addresses.  

---

## 🗄️ Databases  

**Q: Explain the difference between a primary key and a foreign key.**  
- Primary Key: Uniquely identifies a row in a table.  
- Foreign Key: References a primary key in another table to enforce relationships.  

**Q: What are ACID properties in a database system?**  
- Atomicity, Consistency, Isolation, Durability – ensure reliability of transactions.  

**Q: What is normalization? Why is it important?**  
- Organizing tables to reduce redundancy and dependency.  
- Improves efficiency and data integrity.  

**Q: Explain the difference between relational and NoSQL databases.**  
- Relational: Structured, SQL-based, uses tables (MySQL, PostgreSQL).  
- NoSQL: Flexible schema, handles unstructured data (MongoDB, Cassandra).  

**Q: What are triggers in SQL?**  
- Special procedures that automatically execute when certain events occur in a table.  

---

## 👨‍💻 Programming & Software Engineering  

**Q: What are the principles of clean code?**  
- Readability, simplicity, meaningful names, small functions, minimal duplication.  

**Q: Explain DRY, KISS, and YAGNI principles.**  
- DRY: Don’t Repeat Yourself.  
- KISS: Keep It Simple, Stupid.  
- YAGNI: You Aren’t Gonna Need It (avoid overengineering).  

**Q: What is refactoring? Why is it important?**  
- Improving code structure without changing behavior.  
- Important for maintainability and reducing technical debt.  

**Q: What is test-driven development (TDD)?**  
- Write tests before code; ensures correctness and reliability.  

**Q: Explain the importance of version control systems.**  
- Tracks changes, supports collaboration, rollback, and branching (e.g., Git).  

---

## 📊 Management (Robbins & Coulter)  

**Q: What are the four functions of management?**  
- Planning, Organizing, Leading, Controlling.  

**Q: What is the difference between leadership and management?**  
- Management: Focus on processes, structure, efficiency.  
- Leadership: Inspires and motivates people to achieve goals.  

**Q: Explain Maslow’s hierarchy of needs.**  
- Human motivation model: Physiological → Safety → Love/Belonging → Esteem → Self-Actualization.  

**Q: What is the SWOT analysis?**  
- Strengths, Weaknesses, Opportunities, Threats – strategic planning tool.  

**Q: Describe the decision-making process in management.**  
- Identify problem → Gather info → Evaluate alternatives → Choose → Implement → Review.  

---

## 🧮 Mathematics (Linear Algebra, Discrete Math)  

**Q: What is the difference between a vector space and a subspace?**  
- Vector Space: A set closed under vector addition and scalar multiplication.  
- Subspace: A subset of a vector space that is also a vector space.  

**Q: What is an eigenvalue and eigenvector?**  
- Eigenvector: Non-zero vector that changes only in scale after transformation.  
- Eigenvalue: The scale factor corresponding to an eigenvector.  

**Q: What are the basic graph traversal algorithms?**  
- Depth First Search (DFS), Breadth First Search (BFS).  

**Q: Explain Boolean algebra with examples.**  
- Algebra of logic with operators (AND, OR, NOT).  
- Example: A·1 = A, A + 0 = A.  

**Q: What is the difference between permutation and combination?**  
- Permutation: Order matters.  
- Combination: Order does not matter.  

---

## 🔗 Cross-Topic Example  

**Q: Explain the relation between database normalization and algorithm efficiency.**  
- Normalization reduces redundancy, leading to smaller datasets.  
- Algorithms (like search, joins) perform more efficiently on normalized data due to less duplication and structured relationships.  
