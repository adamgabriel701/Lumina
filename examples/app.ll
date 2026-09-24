; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
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
  %"porta" = alloca i64
  store i64 3000, i64* %"porta"
  %"porta_load" = load i64, i64* %"porta"
  %"iniciar_call" = call i64 @"iniciar"(i64 %"porta_load")
  %"server_fd" = alloca i64
  store i64 %"iniciar_call", i64* %"server_fd"
  %"server_fd_load" = load i64, i64* %"server_fd"
  %"icmp" = icmp slt i64 %"server_fd_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %".10" = bitcast [34 x i8]* @"str_0" to i8*
  %"porta_load.1" = load i64, i64* %"porta"
  %".11" = bitcast [4 x i8]* @"str_1" to i8*
  %"num_to_str" = alloca [64 x i8]
  %"num_to_str_ptr" = bitcast [64 x i8]* %"num_to_str" to i8*
  %"num_to_str_call" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"num_to_str_ptr", i64 64, i8* %".11", i64 %"porta_load.1")
  %"sconcat_len1" = call i64 @"strlen"(i8* %".10")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"num_to_str_ptr")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %".10")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"num_to_str_ptr")
  %".12" = bitcast [3 x i8]* @"str_2" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".12", i8* %"sconcat_buf")
  %".13" = bitcast [2 x i8]* @"str_3" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".13")
  %"ret_trunc" = trunc i64 1 to i32
  ret i32 %"ret_trunc"
if_else:
  br label %"if_end"
if_end:
  %".16" = bitcast [42 x i8]* @"str_4" to i8*
  %"porta_load.2" = load i64, i64* %"porta"
  %".17" = bitcast [4 x i8]* @"str_5" to i8*
  %"num_to_str.1" = alloca [64 x i8]
  %"num_to_str_ptr.1" = bitcast [64 x i8]* %"num_to_str.1" to i8*
  %"num_to_str_call.1" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"num_to_str_ptr.1", i64 64, i8* %".17", i64 %"porta_load.2")
  %"sconcat_len1.1" = call i64 @"strlen"(i8* %".16")
  %"sconcat_len2.1" = call i64 @"strlen"(i8* %"num_to_str_ptr.1")
  %"sconcat_sum.1" = add i64 %"sconcat_len1.1", %"sconcat_len2.1"
  %"sconcat_total.1" = add i64 %"sconcat_sum.1", 1
  %"sconcat_buf.1" = call i8* @"GC_malloc"(i64 %"sconcat_total.1")
  %"sconcat_cpy.1" = call i8* @"strcpy"(i8* %"sconcat_buf.1", i8* %".16")
  %"sconcat_cat.1" = call i8* @"strcat"(i8* %"sconcat_buf.1", i8* %"num_to_str_ptr.1")
  %".18" = bitcast [3 x i8]* @"str_6" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".18", i8* %"sconcat_buf.1")
  %".19" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".19")
  %"client_addr_stack" = alloca [16 x i8]
  %"client_addr_first" = getelementptr [16 x i8], [16 x i8]* %"client_addr_stack", i32 0, i32 0
  %"client_addr" = alloca i8*
  store i8* %"client_addr_first", i8** %"client_addr"
  %"client_len_ptr_stack" = alloca [4 x i8]
  %"client_len_ptr_first" = getelementptr [4 x i8], [4 x i8]* %"client_len_ptr_stack", i32 0, i32 0
  %"client_len_ptr" = alloca i8*
  store i8* %"client_len_ptr_first", i8** %"client_len_ptr"
  %"client_len_ptr_load" = load i8*, i8** %"client_len_ptr"
  %"idx_ptr" = getelementptr i8, i8* %"client_len_ptr_load", i64 0
  %"elem_trunc" = trunc i64 16 to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  %"request_buffer_stack" = alloca [1024 x i8]
  %"request_buffer_first" = getelementptr [1024 x i8], [1024 x i8]* %"request_buffer_stack", i32 0, i32 0
  %"request_buffer" = alloca i8*
  store i8* %"request_buffer_first", i8** %"request_buffer"
  %".24" = bitcast [85 x i8]* @"str_8" to i8*
  %"response" = alloca i8*
  store i8* %".24", i8** %"response"
  %"response_load" = load i8*, i8** %"response"
  %"len_str" = call i64 @"strlen"(i8* %"response_load")
  %"resp_len" = alloca i64
  store i64 %"len_str", i64* %"resp_len"
  br label %"while_cond"
while_cond:
  br i1 1, label %"while_body", label %"while_end"
while_body:
  %"server_fd_load.1" = load i64, i64* %"server_fd"
  %"client_addr_load" = load i8*, i8** %"client_addr"
  %"client_len_ptr_load.1" = load i8*, i8** %"client_len_ptr"
  %"accept_call" = call i64 @"accept"(i64 %"server_fd_load.1", i8* %"client_addr_load", i8* %"client_len_ptr_load.1")
  %"client_fd" = alloca i64
  store i64 %"accept_call", i64* %"client_fd"
  %"client_fd_load" = load i64, i64* %"client_fd"
  %"icmp.1" = icmp slt i64 %"client_fd_load", 0
  br i1 %"icmp.1", label %"if_then.1", label %"if_else.1"
while_end:
  %"ret_trunc.1" = trunc i64 0 to i32
  ret i32 %"ret_trunc.1"
if_then.1:
  br label %"while_cond"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"client_fd_load.1" = load i64, i64* %"client_fd"
  %"request_buffer_load" = load i8*, i8** %"request_buffer"
  %"recv_call" = call i64 @"recv"(i64 %"client_fd_load.1", i8* %"request_buffer_load", i64 1024, i64 0)
  %"client_fd_load.2" = load i64, i64* %"client_fd"
  %"response_load.1" = load i8*, i8** %"response"
  %"resp_len_load" = load i64, i64* %"resp_len"
  %"send_call" = call i64 @"send"(i64 %"client_fd_load.2", i8* %"response_load.1", i64 %"resp_len_load", i64 0)
  %"client_fd_load.3" = load i64, i64* %"client_fd"
  %"close_call" = call i64 @"close"(i64 %"client_fd_load.3")
  br label %"while_cond"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
declare i64 @"socket"(i64 %".1", i64 %".2", i64 %".3")

declare i64 @"setsockopt"(i64 %".1", i64 %".2", i64 %".3", i8* %".4", i64 %".5")

declare i64 @"bind"(i64 %".1", i8* %".2", i64 %".3")

declare i64 @"listen"(i64 %".1", i64 %".2")

declare i64 @"accept"(i64 %".1", i8* %".2", i8* %".3")

declare i64 @"recv"(i64 %".1", i8* %".2", i64 %".3", i64 %".4")

declare i64 @"send"(i64 %".1", i8* %".2", i64 %".3", i64 %".4")

declare i64 @"close"(i64 %".1")

define i64 @"iniciar"(i64 %".1")
{
iniciar_entry:
  %"porta" = alloca i64
  store i64 %".1", i64* %"porta"
  br label %"iniciar_body"
iniciar_body:
  %"socket_call" = call i64 @"socket"(i64 2, i64 1, i64 0)
  %"server_fd" = alloca i64
  store i64 %"socket_call", i64* %"server_fd"
  %"server_fd_load" = load i64, i64* %"server_fd"
  %"icmp" = icmp slt i64 %"server_fd_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"neg" = sub i64 0, 1
  ret i64 %"neg"
if_else:
  br label %"if_end"
if_end:
  %"reuse_stack" = alloca [4 x i8]
  %"reuse_first" = getelementptr [4 x i8], [4 x i8]* %"reuse_stack", i32 0, i32 0
  %"reuse" = alloca i8*
  store i8* %"reuse_first", i8** %"reuse"
  %"reuse_load" = load i8*, i8** %"reuse"
  %"idx_ptr" = getelementptr i8, i8* %"reuse_load", i64 0
  %"elem_trunc" = trunc i64 1 to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  %"server_fd_load.1" = load i64, i64* %"server_fd"
  %"reuse_load.1" = load i8*, i8** %"reuse"
  %"setsockopt_call" = call i64 @"setsockopt"(i64 %"server_fd_load.1", i64 1, i64 2, i8* %"reuse_load.1", i64 4)
  %"addr_stack" = alloca [16 x i8]
  %"addr_first" = getelementptr [16 x i8], [16 x i8]* %"addr_stack", i32 0, i32 0
  %"addr" = alloca i8*
  store i8* %"addr_first", i8** %"addr"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"for_cond"
for_cond:
  %"for_curr" = load i64, i64* %"i"
  %"for_cond.1" = icmp slt i64 %"for_curr", 16
  br i1 %"for_cond.1", label %"for_body", label %"for_end"
for_body:
  %"addr_load" = load i8*, i8** %"addr"
  %"i_load" = load i64, i64* %"i"
  %"idx_ptr.1" = getelementptr i8, i8* %"addr_load", i64 %"i_load"
  %"elem_trunc.1" = trunc i64 0 to i8
  store i8 %"elem_trunc.1", i8* %"idx_ptr.1"
  br label %"for_inc"
for_inc:
  %"for_curr_inc" = load i64, i64* %"i"
  %"for_next" = add i64 %"for_curr_inc", 1
  store i64 %"for_next", i64* %"i"
  br label %"for_cond"
for_end:
  %"addr_load.1" = load i8*, i8** %"addr"
  %"idx_ptr.2" = getelementptr i8, i8* %"addr_load.1", i64 0
  %"elem_trunc.2" = trunc i64 2 to i8
  store i8 %"elem_trunc.2", i8* %"idx_ptr.2"
  %"porta_load" = load i64, i64* %"porta"
  %"div" = sdiv i64 %"porta_load", 256
  %"addr_load.2" = load i8*, i8** %"addr"
  %"idx_ptr.3" = getelementptr i8, i8* %"addr_load.2", i64 2
  %"elem_trunc.3" = trunc i64 %"div" to i8
  store i8 %"elem_trunc.3", i8* %"idx_ptr.3"
  %"porta_load.1" = load i64, i64* %"porta"
  %"mod" = srem i64 %"porta_load.1", 256
  %"addr_load.3" = load i8*, i8** %"addr"
  %"idx_ptr.4" = getelementptr i8, i8* %"addr_load.3", i64 3
  %"elem_trunc.4" = trunc i64 %"mod" to i8
  store i8 %"elem_trunc.4", i8* %"idx_ptr.4"
  %"server_fd_load.2" = load i64, i64* %"server_fd"
  %"addr_load.4" = load i8*, i8** %"addr"
  %"bind_call" = call i64 @"bind"(i64 %"server_fd_load.2", i8* %"addr_load.4", i64 16)
  %"bind_res" = alloca i64
  store i64 %"bind_call", i64* %"bind_res"
  %"bind_res_load" = load i64, i64* %"bind_res"
  %"icmp.1" = icmp slt i64 %"bind_res_load", 0
  br i1 %"icmp.1", label %"if_then.1", label %"if_else.1"
if_then.1:
  %"server_fd_load.3" = load i64, i64* %"server_fd"
  %"close_call" = call i64 @"close"(i64 %"server_fd_load.3")
  %"neg.1" = sub i64 0, 1
  ret i64 %"neg.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"server_fd_load.4" = load i64, i64* %"server_fd"
  %"listen_call" = call i64 @"listen"(i64 %"server_fd_load.4", i64 10)
  %"server_fd_load.5" = load i64, i64* %"server_fd"
  ret i64 %"server_fd_load.5"
}

define void @"responder"(i64 %".1", i8* %".2")
{
responder_entry:
  %"client_fd" = alloca i64
  store i64 %".1", i64* %"client_fd"
  %"body" = alloca i8*
  store i8* %".2", i8** %"body"
  br label %"responder_body"
responder_body:
  %".7" = bitcast [59 x i8]* @"str_9" to i8*
  %"body_load" = load i8*, i8** %"body"
  %"len_str" = call i64 @"strlen"(i8* %"body_load")
  %".8" = bitcast [4 x i8]* @"str_10" to i8*
  %"num_to_str" = alloca [64 x i8]
  %"num_to_str_ptr" = bitcast [64 x i8]* %"num_to_str" to i8*
  %"num_to_str_call" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"num_to_str_ptr", i64 64, i8* %".8", i64 %"len_str")
  %"sconcat_len1" = call i64 @"strlen"(i8* %".7")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"num_to_str_ptr")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %".7")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"num_to_str_ptr")
  %".9" = bitcast [24 x i8]* @"str_11" to i8*
  %"sconcat_len1.1" = call i64 @"strlen"(i8* %"sconcat_buf")
  %"sconcat_len2.1" = call i64 @"strlen"(i8* %".9")
  %"sconcat_sum.1" = add i64 %"sconcat_len1.1", %"sconcat_len2.1"
  %"sconcat_total.1" = add i64 %"sconcat_sum.1", 1
  %"sconcat_buf.1" = call i8* @"GC_malloc"(i64 %"sconcat_total.1")
  %"sconcat_cpy.1" = call i8* @"strcpy"(i8* %"sconcat_buf.1", i8* %"sconcat_buf")
  %"sconcat_cat.1" = call i8* @"strcat"(i8* %"sconcat_buf.1", i8* %".9")
  %"body_load.1" = load i8*, i8** %"body"
  %"sconcat_len1.2" = call i64 @"strlen"(i8* %"sconcat_buf.1")
  %"sconcat_len2.2" = call i64 @"strlen"(i8* %"body_load.1")
  %"sconcat_sum.2" = add i64 %"sconcat_len1.2", %"sconcat_len2.2"
  %"sconcat_total.2" = add i64 %"sconcat_sum.2", 1
  %"sconcat_buf.2" = call i8* @"GC_malloc"(i64 %"sconcat_total.2")
  %"sconcat_cpy.2" = call i8* @"strcpy"(i8* %"sconcat_buf.2", i8* %"sconcat_buf.1")
  %"sconcat_cat.2" = call i8* @"strcat"(i8* %"sconcat_buf.2", i8* %"body_load.1")
  %"header" = alloca i8*
  store i8* %"sconcat_buf.2", i8** %"header"
  %"client_fd_load" = load i64, i64* %"client_fd"
  %"header_load" = load i8*, i8** %"header"
  %"header_load.1" = load i8*, i8** %"header"
  %"len_str.1" = call i64 @"strlen"(i8* %"header_load.1")
  %"send_call" = call i64 @"send"(i64 %"client_fd_load", i8* %"header_load", i64 %"len_str.1", i64 0)
  %"client_fd_load.1" = load i64, i64* %"client_fd"
  %"close_call" = call i64 @"close"(i64 %"client_fd_load.1")
  ret void
}

define void @"not_found"(i64 %".1")
{
not_found_entry:
  %"client_fd" = alloca i64
  store i64 %".1", i64* %"client_fd"
  br label %"not_found_body"
not_found_body:
  %".5" = bitcast [37 x i8]* @"str_12" to i8*
  %"body" = alloca i8*
  store i8* %".5", i8** %"body"
  %".7" = bitcast [66 x i8]* @"str_13" to i8*
  %"body_load" = load i8*, i8** %"body"
  %"len_str" = call i64 @"strlen"(i8* %"body_load")
  %".8" = bitcast [4 x i8]* @"str_14" to i8*
  %"num_to_str" = alloca [64 x i8]
  %"num_to_str_ptr" = bitcast [64 x i8]* %"num_to_str" to i8*
  %"num_to_str_call" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"num_to_str_ptr", i64 64, i8* %".8", i64 %"len_str")
  %"sconcat_len1" = call i64 @"strlen"(i8* %".7")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"num_to_str_ptr")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %".7")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"num_to_str_ptr")
  %".9" = bitcast [24 x i8]* @"str_15" to i8*
  %"sconcat_len1.1" = call i64 @"strlen"(i8* %"sconcat_buf")
  %"sconcat_len2.1" = call i64 @"strlen"(i8* %".9")
  %"sconcat_sum.1" = add i64 %"sconcat_len1.1", %"sconcat_len2.1"
  %"sconcat_total.1" = add i64 %"sconcat_sum.1", 1
  %"sconcat_buf.1" = call i8* @"GC_malloc"(i64 %"sconcat_total.1")
  %"sconcat_cpy.1" = call i8* @"strcpy"(i8* %"sconcat_buf.1", i8* %"sconcat_buf")
  %"sconcat_cat.1" = call i8* @"strcat"(i8* %"sconcat_buf.1", i8* %".9")
  %"body_load.1" = load i8*, i8** %"body"
  %"sconcat_len1.2" = call i64 @"strlen"(i8* %"sconcat_buf.1")
  %"sconcat_len2.2" = call i64 @"strlen"(i8* %"body_load.1")
  %"sconcat_sum.2" = add i64 %"sconcat_len1.2", %"sconcat_len2.2"
  %"sconcat_total.2" = add i64 %"sconcat_sum.2", 1
  %"sconcat_buf.2" = call i8* @"GC_malloc"(i64 %"sconcat_total.2")
  %"sconcat_cpy.2" = call i8* @"strcpy"(i8* %"sconcat_buf.2", i8* %"sconcat_buf.1")
  %"sconcat_cat.2" = call i8* @"strcat"(i8* %"sconcat_buf.2", i8* %"body_load.1")
  %"header" = alloca i8*
  store i8* %"sconcat_buf.2", i8** %"header"
  %"client_fd_load" = load i64, i64* %"client_fd"
  %"header_load" = load i8*, i8** %"header"
  %"header_load.1" = load i8*, i8** %"header"
  %"len_str.1" = call i64 @"strlen"(i8* %"header_load.1")
  %"send_call" = call i64 @"send"(i64 %"client_fd_load", i8* %"header_load", i64 %"len_str.1", i64 0)
  %"client_fd_load.1" = load i64, i64* %"client_fd"
  %"close_call" = call i64 @"close"(i64 %"client_fd_load.1")
  ret void
}

@"str_0" = constant [34 x i8] c"Erro ao iniciar backend na porta \00"
@"str_1" = constant [4 x i8] c"%ld\00"
@"str_2" = constant [3 x i8] c"%s\00"
@"str_3" = constant [2 x i8] c"\0a\00"
@"str_4" = constant [42 x i8] c"\f0\9f\9f\a2 Backend rodando em http://localhost:\00"
@"str_5" = constant [4 x i8] c"%ld\00"
@"str_6" = constant [3 x i8] c"%s\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [85 x i8] c"HTTP/1.1 200 OK\0d\0aContent-Type: text/html\0d\0aContent-Length: 20\0d\0a\0d\0a<h1>Backend OK!</h1>\00"
@"str_9" = constant [59 x i8] c"HTTP/1.1 200 OK\0d\0aContent-Type: text/html\0d\0aContent-Length: \00"
@"str_10" = constant [4 x i8] c"%ld\00"
@"str_11" = constant [24 x i8] c"\0d\0aConnection: close\0d\0a\0d\0a\00"
@"str_12" = constant [37 x i8] c"<h1>404 - Pagina Nao Encontrada</h1>\00"
@"str_13" = constant [66 x i8] c"HTTP/1.1 404 Not Found\0d\0aContent-Type: text/html\0d\0aContent-Length: \00"
@"str_14" = constant [4 x i8] c"%ld\00"
@"str_15" = constant [24 x i8] c"\0d\0aConnection: close\0d\0a\0d\0a\00"