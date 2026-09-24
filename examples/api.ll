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
  store i64 8080, i64* %"porta"
  %"porta_load" = load i64, i64* %"porta"
  %"iniciar_call" = call i64 @"iniciar"(i64 %"porta_load")
  %"server_fd" = alloca i64
  store i64 %"iniciar_call", i64* %"server_fd"
  %"server_fd_load" = load i64, i64* %"server_fd"
  %"icmp" = icmp slt i64 %"server_fd_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"ret_trunc" = trunc i64 1 to i32
  ret i32 %"ret_trunc"
if_else:
  br label %"if_end"
if_end:
  %".12" = bitcast [42 x i8]* @"str_0" to i8*
  %"porta_load.1" = load i64, i64* %"porta"
  %".13" = bitcast [4 x i8]* @"str_1" to i8*
  %"num_to_str" = alloca [64 x i8]
  %"num_to_str_ptr" = bitcast [64 x i8]* %"num_to_str" to i8*
  %"num_to_str_call" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"num_to_str_ptr", i64 64, i8* %".13", i64 %"porta_load.1")
  %"sconcat_len1" = call i64 @"strlen"(i8* %".12")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"num_to_str_ptr")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %".12")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"num_to_str_ptr")
  %".14" = bitcast [3 x i8]* @"str_2" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".14", i8* %"sconcat_buf")
  %".15" = bitcast [2 x i8]* @"str_3" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".15")
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
  %".20" = bitcast [78 x i8]* @"str_4" to i8*
  %"home_resp" = alloca i8*
  store i8* %".20", i8** %"home_resp"
  %".22" = bitcast [91 x i8]* @"str_5" to i8*
  %"api_resp" = alloca i8*
  store i8* %".22", i8** %"api_resp"
  %".24" = bitcast [94 x i8]* @"str_6" to i8*
  %"not_found_resp" = alloca i8*
  store i8* %".24", i8** %"not_found_resp"
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
  %"request_buffer_load.1" = load i8*, i8** %"request_buffer"
  %".32" = getelementptr i8, i8* %"request_buffer_load.1", i64 0
  %"ptr_idx_load" = load i8, i8* %".32"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"icmp.2" = icmp eq i64 %"idx_sext", 71
  br i1 %"icmp.2", label %"and_rhs", label %"and_end"
and_rhs:
  %"request_buffer_load.2" = load i8*, i8** %"request_buffer"
  %".34" = getelementptr i8, i8* %"request_buffer_load.2", i64 1
  %"ptr_idx_load.1" = load i8, i8* %".34"
  %"idx_sext.1" = sext i8 %"ptr_idx_load.1" to i64
  %"icmp.3" = icmp eq i64 %"idx_sext.1", 69
  br label %"and_end"
and_end:
  %"and_result" = phi  i1 [0, %"if_end.1"], [%"icmp.3", %"and_rhs"]
  br i1 %"and_result", label %"and_rhs.1", label %"and_end.1"
and_rhs.1:
  %"request_buffer_load.3" = load i8*, i8** %"request_buffer"
  %".37" = getelementptr i8, i8* %"request_buffer_load.3", i64 2
  %"ptr_idx_load.2" = load i8, i8* %".37"
  %"idx_sext.2" = sext i8 %"ptr_idx_load.2" to i64
  %"icmp.4" = icmp eq i64 %"idx_sext.2", 84
  br label %"and_end.1"
and_end.1:
  %"and_result.1" = phi  i1 [0, %"and_end"], [%"icmp.4", %"and_rhs.1"]
  br i1 %"and_result.1", label %"and_rhs.2", label %"and_end.2"
and_rhs.2:
  %"request_buffer_load.4" = load i8*, i8** %"request_buffer"
  %".40" = getelementptr i8, i8* %"request_buffer_load.4", i64 3
  %"ptr_idx_load.3" = load i8, i8* %".40"
  %"idx_sext.3" = sext i8 %"ptr_idx_load.3" to i64
  %"icmp.5" = icmp eq i64 %"idx_sext.3", 32
  br label %"and_end.2"
and_end.2:
  %"and_result.2" = phi  i1 [0, %"and_end.1"], [%"icmp.5", %"and_rhs.2"]
  br i1 %"and_result.2", label %"and_rhs.3", label %"and_end.3"
and_rhs.3:
  %"request_buffer_load.5" = load i8*, i8** %"request_buffer"
  %".43" = getelementptr i8, i8* %"request_buffer_load.5", i64 4
  %"ptr_idx_load.4" = load i8, i8* %".43"
  %"idx_sext.4" = sext i8 %"ptr_idx_load.4" to i64
  %"icmp.6" = icmp eq i64 %"idx_sext.4", 47
  br label %"and_end.3"
and_end.3:
  %"and_result.3" = phi  i1 [0, %"and_end.2"], [%"icmp.6", %"and_rhs.3"]
  br i1 %"and_result.3", label %"and_rhs.4", label %"and_end.4"
and_rhs.4:
  %"request_buffer_load.6" = load i8*, i8** %"request_buffer"
  %".46" = getelementptr i8, i8* %"request_buffer_load.6", i64 5
  %"ptr_idx_load.5" = load i8, i8* %".46"
  %"idx_sext.5" = sext i8 %"ptr_idx_load.5" to i64
  %"icmp.7" = icmp eq i64 %"idx_sext.5", 32
  br label %"and_end.4"
and_end.4:
  %"and_result.4" = phi  i1 [0, %"and_end.3"], [%"icmp.7", %"and_rhs.4"]
  br i1 %"and_result.4", label %"if_then.2", label %"if_else.2"
if_then.2:
  %"client_fd_load.2" = load i64, i64* %"client_fd"
  %"home_resp_load" = load i8*, i8** %"home_resp"
  %"home_resp_load.1" = load i8*, i8** %"home_resp"
  %"len_str" = call i64 @"strlen"(i8* %"home_resp_load.1")
  %"send_call" = call i64 @"send"(i64 %"client_fd_load.2", i8* %"home_resp_load", i64 %"len_str", i64 0)
  %"client_fd_load.3" = load i64, i64* %"client_fd"
  %"close_call" = call i64 @"close"(i64 %"client_fd_load.3")
  br label %"while_cond"
if_else.2:
  br label %"if_end.2"
if_end.2:
  %"request_buffer_load.7" = load i8*, i8** %"request_buffer"
  %".51" = getelementptr i8, i8* %"request_buffer_load.7", i64 0
  %"ptr_idx_load.6" = load i8, i8* %".51"
  %"idx_sext.6" = sext i8 %"ptr_idx_load.6" to i64
  %"icmp.8" = icmp eq i64 %"idx_sext.6", 71
  br i1 %"icmp.8", label %"and_rhs.5", label %"and_end.5"
and_rhs.5:
  %"request_buffer_load.8" = load i8*, i8** %"request_buffer"
  %".53" = getelementptr i8, i8* %"request_buffer_load.8", i64 1
  %"ptr_idx_load.7" = load i8, i8* %".53"
  %"idx_sext.7" = sext i8 %"ptr_idx_load.7" to i64
  %"icmp.9" = icmp eq i64 %"idx_sext.7", 69
  br label %"and_end.5"
and_end.5:
  %"and_result.5" = phi  i1 [0, %"if_end.2"], [%"icmp.9", %"and_rhs.5"]
  br i1 %"and_result.5", label %"and_rhs.6", label %"and_end.6"
and_rhs.6:
  %"request_buffer_load.9" = load i8*, i8** %"request_buffer"
  %".56" = getelementptr i8, i8* %"request_buffer_load.9", i64 2
  %"ptr_idx_load.8" = load i8, i8* %".56"
  %"idx_sext.8" = sext i8 %"ptr_idx_load.8" to i64
  %"icmp.10" = icmp eq i64 %"idx_sext.8", 84
  br label %"and_end.6"
and_end.6:
  %"and_result.6" = phi  i1 [0, %"and_end.5"], [%"icmp.10", %"and_rhs.6"]
  br i1 %"and_result.6", label %"and_rhs.7", label %"and_end.7"
and_rhs.7:
  %"request_buffer_load.10" = load i8*, i8** %"request_buffer"
  %".59" = getelementptr i8, i8* %"request_buffer_load.10", i64 3
  %"ptr_idx_load.9" = load i8, i8* %".59"
  %"idx_sext.9" = sext i8 %"ptr_idx_load.9" to i64
  %"icmp.11" = icmp eq i64 %"idx_sext.9", 32
  br label %"and_end.7"
and_end.7:
  %"and_result.7" = phi  i1 [0, %"and_end.6"], [%"icmp.11", %"and_rhs.7"]
  br i1 %"and_result.7", label %"and_rhs.8", label %"and_end.8"
and_rhs.8:
  %"request_buffer_load.11" = load i8*, i8** %"request_buffer"
  %".62" = getelementptr i8, i8* %"request_buffer_load.11", i64 4
  %"ptr_idx_load.10" = load i8, i8* %".62"
  %"idx_sext.10" = sext i8 %"ptr_idx_load.10" to i64
  %"icmp.12" = icmp eq i64 %"idx_sext.10", 47
  br label %"and_end.8"
and_end.8:
  %"and_result.8" = phi  i1 [0, %"and_end.7"], [%"icmp.12", %"and_rhs.8"]
  br i1 %"and_result.8", label %"and_rhs.9", label %"and_end.9"
and_rhs.9:
  %"request_buffer_load.12" = load i8*, i8** %"request_buffer"
  %".65" = getelementptr i8, i8* %"request_buffer_load.12", i64 5
  %"ptr_idx_load.11" = load i8, i8* %".65"
  %"idx_sext.11" = sext i8 %"ptr_idx_load.11" to i64
  %"icmp.13" = icmp eq i64 %"idx_sext.11", 97
  br label %"and_end.9"
and_end.9:
  %"and_result.9" = phi  i1 [0, %"and_end.8"], [%"icmp.13", %"and_rhs.9"]
  br i1 %"and_result.9", label %"if_then.3", label %"if_else.3"
if_then.3:
  %"client_fd_load.4" = load i64, i64* %"client_fd"
  %"api_resp_load" = load i8*, i8** %"api_resp"
  %"api_resp_load.1" = load i8*, i8** %"api_resp"
  %"len_str.1" = call i64 @"strlen"(i8* %"api_resp_load.1")
  %"send_call.1" = call i64 @"send"(i64 %"client_fd_load.4", i8* %"api_resp_load", i64 %"len_str.1", i64 0)
  %"client_fd_load.5" = load i64, i64* %"client_fd"
  %"close_call.1" = call i64 @"close"(i64 %"client_fd_load.5")
  br label %"while_cond"
if_else.3:
  br label %"if_end.3"
if_end.3:
  %"client_fd_load.6" = load i64, i64* %"client_fd"
  %"not_found_resp_load" = load i8*, i8** %"not_found_resp"
  %"not_found_resp_load.1" = load i8*, i8** %"not_found_resp"
  %"len_str.2" = call i64 @"strlen"(i8* %"not_found_resp_load.1")
  %"send_call.2" = call i64 @"send"(i64 %"client_fd_load.6", i8* %"not_found_resp_load", i64 %"len_str.2", i64 0)
  %"client_fd_load.7" = load i64, i64* %"client_fd"
  %"close_call.2" = call i64 @"close"(i64 %"client_fd_load.7")
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
  %".7" = bitcast [59 x i8]* @"str_7" to i8*
  %"body_load" = load i8*, i8** %"body"
  %"len_str" = call i64 @"strlen"(i8* %"body_load")
  %".8" = bitcast [4 x i8]* @"str_8" to i8*
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
  %".9" = bitcast [24 x i8]* @"str_9" to i8*
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
  %".5" = bitcast [37 x i8]* @"str_10" to i8*
  %"body" = alloca i8*
  store i8* %".5", i8** %"body"
  %".7" = bitcast [66 x i8]* @"str_11" to i8*
  %"body_load" = load i8*, i8** %"body"
  %"len_str" = call i64 @"strlen"(i8* %"body_load")
  %".8" = bitcast [4 x i8]* @"str_12" to i8*
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
  %".9" = bitcast [24 x i8]* @"str_13" to i8*
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

@"str_0" = constant [42 x i8] c"Servidor API rodando em http://localhost:\00"
@"str_1" = constant [4 x i8] c"%ld\00"
@"str_2" = constant [3 x i8] c"%s\00"
@"str_3" = constant [2 x i8] c"\0a\00"
@"str_4" = constant [78 x i8] c"HTTP/1.1 200 OK\0d\0aContent-Type: text/html\0d\0aContent-Length: 13\0d\0a\0d\0a<h1>Home</h1>\00"
@"str_5" = constant [91 x i8] c"HTTP/1.1 200 OK\0d\0aContent-Type: application/json\0d\0aContent-Length: 19\0d\0a\0d\0a{\22status\22:\22online\22}\00"
@"str_6" = constant [94 x i8] c"HTTP/1.1 404 Not Found\0d\0aContent-Type: text/html\0d\0aContent-Length: 22\0d\0a\0d\0a<h1>404 Not Found</h1>\00"
@"str_7" = constant [59 x i8] c"HTTP/1.1 200 OK\0d\0aContent-Type: text/html\0d\0aContent-Length: \00"
@"str_8" = constant [4 x i8] c"%ld\00"
@"str_9" = constant [24 x i8] c"\0d\0aConnection: close\0d\0a\0d\0a\00"
@"str_10" = constant [37 x i8] c"<h1>404 - Pagina Nao Encontrada</h1>\00"
@"str_11" = constant [66 x i8] c"HTTP/1.1 404 Not Found\0d\0aContent-Type: text/html\0d\0aContent-Length: \00"
@"str_12" = constant [4 x i8] c"%ld\00"
@"str_13" = constant [24 x i8] c"\0d\0aConnection: close\0d\0a\0d\0a\00"