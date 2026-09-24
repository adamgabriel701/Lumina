; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
%"Node" = type {i64, i64*}
%"List" = type {i64*, i64}
declare i32 @"printf"(i8* %".1", ...)

declare i8* @"GC_malloc"(i64 %".1")

declare void @"GC_init"()

declare void @"GC_free"(i8* %".1")

declare i8* @"strcpy"(i8* %".1", i8* %".2")

declare i8* @"strcat"(i8* %".1", i8* %".2")

declare i64 @"strlen"(i8* %".1")

declare i32 @"snprintf"(i8* %".1", i64 %".2", i8* %".3", ...)

declare i8* @"strstr"(i8* %".1", i8* %".2")

declare i32 @"strncmp"(i8* %".1", i8* %".2", i64 %".3")

declare i64 @"atoi"(i8* %".1")

declare i32 @"strcmp"(i8* %".1", i8* %".2")

declare i8* @"strncpy"(i8* %".1", i8* %".2", i64 %".3")

@"stdin" = external global i8*
@"stdout" = external global i8*
@"stderr" = external global i8*
define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [36 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"new_call" = call %"List"* @"new"()
  %"l" = alloca %"List"*
  store %"List"* %"new_call", %"List"** %"l"
  %"l_load" = load %"List"*, %"List"** %"l"
  call void @"push"(%"List"* %"l_load", i64 10)
  %"l_load.1" = load %"List"*, %"List"** %"l"
  call void @"push"(%"List"* %"l_load.1", i64 20)
  %"l_load.2" = load %"List"*, %"List"** %"l"
  call void @"push"(%"List"* %"l_load.2", i64 30)
  %".11" = bitcast [18 x i8]* @"str_3" to i8*
  %".12" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".12", i8* %".11")
  %"l_load.3" = load %"List"*, %"List"** %"l"
  %".13" = getelementptr %"List", %"List"* %"l_load.3", i32 0, i32 1
  %"size_load" = load i64, i64* %".13"
  %".14" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".14")
  %".15" = bitcast [4 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".15", i64 %"size_load")
  %".16" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".16")
  %".17" = bitcast [12 x i8]* @"str_8" to i8*
  %".18" = bitcast [3 x i8]* @"str_9" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".18", i8* %".17")
  %"l_load.4" = load %"List"*, %"List"** %"l"
  %"get_call" = call i64 @"get"(%"List"* %"l_load.4", i64 0)
  %".19" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".19")
  %".20" = bitcast [4 x i8]* @"str_11" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".20", i64 %"get_call")
  %".21" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".21")
  %".22" = bitcast [12 x i8]* @"str_13" to i8*
  %".23" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".23", i8* %".22")
  %"l_load.5" = load %"List"*, %"List"** %"l"
  %"get_call.1" = call i64 @"get"(%"List"* %"l_load.5", i64 1)
  %".24" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".24")
  %".25" = bitcast [4 x i8]* @"str_16" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".25", i64 %"get_call.1")
  %".26" = bitcast [2 x i8]* @"str_17" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".26")
  %".27" = bitcast [12 x i8]* @"str_18" to i8*
  %".28" = bitcast [3 x i8]* @"str_19" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".28", i8* %".27")
  %"l_load.6" = load %"List"*, %"List"** %"l"
  %"get_call.2" = call i64 @"get"(%"List"* %"l_load.6", i64 2)
  %".29" = bitcast [2 x i8]* @"str_20" to i8*
  %"print_sep.3" = call i32 (i8*, ...) @"printf"(i8* %".29")
  %".30" = bitcast [4 x i8]* @"str_21" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".30", i64 %"get_call.2")
  %".31" = bitcast [2 x i8]* @"str_22" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".31")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
define %"List"* @"new"()
{
new_entry:
  br label %"new_body"
new_body:
  %"l" = alloca %"List"*
  %"l_storage_raw" = call i8* @"GC_malloc"(i64 16)
  %"l_storage" = bitcast i8* %"l_storage_raw" to %"List"*
  store %"List" {i64* null, i64 0}, %"List"* %"l_storage"
  store %"List"* %"l_storage", %"List"** %"l"
  %"l_load" = load %"List"*, %"List"** %"l"
  %"head_ptr" = getelementptr %"List", %"List"* %"l_load", i32 0, i32 0
  %"head_inttoptr" = inttoptr i64 0 to i64*
  store i64* %"head_inttoptr", i64** %"head_ptr"
  %"l_load.1" = load %"List"*, %"List"** %"l"
  %"size_ptr" = getelementptr %"List", %"List"* %"l_load.1", i32 0, i32 1
  store i64 0, i64* %"size_ptr"
  %"l_load.2" = load %"List"*, %"List"** %"l"
  ret %"List"* %"l_load.2"
}

define void @"push"(%"List"* %".1", i64 %".2")
{
push_entry:
  %"l" = alloca %"List"*
  store %"List"* %".1", %"List"** %"l"
  %"val" = alloca i64
  store i64 %".2", i64* %"val"
  br label %"push_body"
push_body:
  %"alloc_bytes_call" = call i8* @"GC_malloc"(i64 16)
  %"new_node" = alloca i64
  %"str_to_int_call" = call i64 @"atoi"(i8* %"alloc_bytes_call")
  store i64 %"str_to_int_call", i64* %"new_node"
  %"val_load" = load i64, i64* %"val"
  %"new_node_load" = load i64, i64* %"new_node"
  %"new_node_load.1" = load i64, i64* %"new_node"
  %"l_load" = load %"List"*, %"List"** %"l"
  %".8" = getelementptr %"List", %"List"* %"l_load", i32 0, i32 0
  %"head_load" = load i64*, i64** %".8"
  %"bin_ptrtoint_l" = ptrtoint i64* %"head_load" to i64
  %"icmp" = icmp eq i64 %"bin_ptrtoint_l", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"new_node_load.2" = load i64, i64* %"new_node"
  %"l_load.1" = load %"List"*, %"List"** %"l"
  %"head_ptr" = getelementptr %"List", %"List"* %"l_load.1", i32 0, i32 0
  %"head_inttoptr" = inttoptr i64 %"new_node_load.2" to i64*
  store i64* %"head_inttoptr", i64** %"head_ptr"
  br label %"if_end"
if_else:
  %"l_load.2" = load %"List"*, %"List"** %"l"
  %".12" = getelementptr %"List", %"List"* %"l_load.2", i32 0, i32 0
  %"head_load.1" = load i64*, i64** %".12"
  %"curr" = alloca i64*
  store i64* %"head_load.1", i64** %"curr"
  br label %"while_cond"
if_end:
  %"l_load.3" = load %"List"*, %"List"** %"l"
  %".24" = getelementptr %"List", %"List"* %"l_load.3", i32 0, i32 1
  %"size_load" = load i64, i64* %".24"
  %"add" = add i64 %"size_load", 1
  %"l_load.4" = load %"List"*, %"List"** %"l"
  %"size_ptr" = getelementptr %"List", %"List"* %"l_load.4", i32 0, i32 1
  store i64 %"add", i64* %"size_ptr"
  ret void
while_cond:
  %"curr_load" = load i64*, i64** %"curr"
  %"bin_ptrtoint_l.1" = ptrtoint i64* %"curr_load" to i64
  %"icmp.1" = icmp ne i64 %"bin_ptrtoint_l.1", 0
  br i1 %"icmp.1", label %"while_body", label %"while_end"
while_body:
  %"curr_load.1" = load i64*, i64** %"curr"
  %"curr_ptr" = alloca i64
  %"ptrtoint_cast" = ptrtoint i64* %"curr_load.1" to i64
  store i64 %"ptrtoint_cast", i64* %"curr_ptr"
  %"curr_ptr_load" = load i64, i64* %"curr_ptr"
  %"next_val" = alloca i64
  store i64 0, i64* %"next_val"
  %"next_val_load" = load i64, i64* %"next_val"
  %"icmp.2" = icmp eq i64 %"next_val_load", 0
  br i1 %"icmp.2", label %"if_then.1", label %"if_else.1"
while_end:
  br label %"if_end"
if_then.1:
  %"new_node_load.3" = load i64, i64* %"new_node"
  %"curr_ptr_load.1" = load i64, i64* %"curr_ptr"
  br label %"while_end"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"next_val_load.1" = load i64, i64* %"next_val"
  %"curr_inttoptr" = inttoptr i64 %"next_val_load.1" to i64*
  store i64* %"curr_inttoptr", i64** %"curr"
  br label %"while_cond"
}

define i64 @"get"(%"List"* %".1", i64 %".2")
{
get_entry:
  %"l" = alloca %"List"*
  store %"List"* %".1", %"List"** %"l"
  %"index" = alloca i64
  store i64 %".2", i64* %"index"
  br label %"get_body"
get_body:
  %"l_load" = load %"List"*, %"List"** %"l"
  %".7" = getelementptr %"List", %"List"* %"l_load", i32 0, i32 0
  %"head_load" = load i64*, i64** %".7"
  %"curr" = alloca i64*
  store i64* %"head_load", i64** %"curr"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"index_load" = load i64, i64* %"index"
  %"icmp" = icmp slt i64 %"i_load", %"index_load"
  br i1 %"icmp", label %"and_rhs", label %"and_end"
while_body:
  %"curr_load.1" = load i64*, i64** %"curr"
  %"curr_ptr" = alloca i64
  %"ptrtoint_cast" = ptrtoint i64* %"curr_load.1" to i64
  store i64 %"ptrtoint_cast", i64* %"curr_ptr"
  %"curr_ptr_load" = load i64, i64* %"curr_ptr"
  %"curr_inttoptr" = inttoptr i64 0 to i64*
  store i64* %"curr_inttoptr", i64** %"curr"
  %"i_load.1" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.1", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
while_end:
  %"curr_load.2" = load i64*, i64** %"curr"
  %"bin_ptrtoint_l.1" = ptrtoint i64* %"curr_load.2" to i64
  %"icmp.2" = icmp ne i64 %"bin_ptrtoint_l.1", 0
  br i1 %"icmp.2", label %"if_then", label %"if_else"
and_rhs:
  %"curr_load" = load i64*, i64** %"curr"
  %"bin_ptrtoint_l" = ptrtoint i64* %"curr_load" to i64
  %"icmp.1" = icmp ne i64 %"bin_ptrtoint_l", 0
  br label %"and_end"
and_end:
  %"and_result" = phi  i1 [0, %"while_cond"], [%"icmp.1", %"and_rhs"]
  br i1 %"and_result", label %"while_body", label %"while_end"
if_then:
  %"curr_load.3" = load i64*, i64** %"curr"
  %"curr_ptr.1" = alloca i64
  %"ptrtoint_cast.1" = ptrtoint i64* %"curr_load.3" to i64
  store i64 %"ptrtoint_cast.1", i64* %"curr_ptr.1"
  %"curr_ptr_load.1" = load i64, i64* %"curr_ptr.1"
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %"neg" = sub i64 0, 1
  ret i64 %"neg"
}

@"str_0" = constant [36 x i8] c"\f0\9f\9a\80 Testando Linked List Nativa...\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [18 x i8] c"Tamanho da lista:\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [4 x i8] c"%ld\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [12 x i8] c"Elemento 0:\00"
@"str_9" = constant [3 x i8] c"%s\00"
@"str_10" = constant [2 x i8] c" \00"
@"str_11" = constant [4 x i8] c"%ld\00"
@"str_12" = constant [2 x i8] c"\0a\00"
@"str_13" = constant [12 x i8] c"Elemento 1:\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c" \00"
@"str_16" = constant [4 x i8] c"%ld\00"
@"str_17" = constant [2 x i8] c"\0a\00"
@"str_18" = constant [12 x i8] c"Elemento 2:\00"
@"str_19" = constant [3 x i8] c"%s\00"
@"str_20" = constant [2 x i8] c" \00"
@"str_21" = constant [4 x i8] c"%ld\00"
@"str_22" = constant [2 x i8] c"\0a\00"